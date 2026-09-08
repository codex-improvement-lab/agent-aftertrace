"""The query process reads one local trace and emits one JSON document."""
import argparse
import json
import sys

from . import __version__
from .query import QueryError, Trace, finite_number, strict_json


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise QueryError("invalid_arguments", message)


def positive(value):
    number = int(value)
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError("limit must be between 1 and 100")
    return number


def offset_value(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("offset cannot be negative")
    return number


def build_parser():
    parser = Parser(description="Read-only, bounded queries over VizTracer 1.1.1 JSON.")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "calls", "history", "first"):
        item = sub.add_parser(name)
        item.add_argument("trace", help="local JSON recording (at most 32 MiB)")
        if name == "calls":
            item.add_argument("--function", help="exact recorded function name")
        if name in ("calls", "history"):
            item.add_argument("--offset", type=offset_value, default=0)
            item.add_argument("--limit", type=positive, default=20)
        if name in ("history", "first"):
            item.add_argument("--var", required=True, help="exact variable name")
            item.add_argument("--call", help="recorded call ID; selects function execution steps")
            item.add_argument("--pid")
            item.add_argument("--tid")
        if name == "first":
            item.add_argument("--op", choices=["eq", "ne", "lt", "le", "gt", "ge"], required=True)
            item.add_argument("--value", required=True, help="JSON scalar; comparisons never evaluate code")
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        value = None
        if args.command == "first":
            if len(args.value) > 4096:
                raise QueryError("invalid_value", "Comparison scalar exceeds 4096 characters.")
            try:
                value = strict_json(args.value)
            except (ValueError, RecursionError) as error:
                raise QueryError("invalid_value", "Supply a JSON scalar, not Python code.") from error
            if not (type(value) in (str, bool, type(None)) or finite_number(value)):
                raise QueryError("invalid_value", "Comparison supports only finite JSON scalars.")
        if args.command in ("history", "first") and (
                not args.var.isidentifier() or len(args.var) > 128):
            raise QueryError("invalid_variable", "Supply one variable identifier, not an expression.")
        trace = Trace(args.trace)
        code = 0
        if args.command == "inspect":
            result = trace.inspect()
        elif args.command == "calls":
            result = trace.list_calls(args.function, args.offset, args.limit)
        elif args.command == "history":
            result, code = trace.history(args.var, args.call, args.pid, args.tid, args.offset, args.limit)
        else:
            result, code = trace.first(args.var, args.op, value, args.call, args.pid, args.tid)
    except QueryError as error:
        result = {"schema": "aftertrace/1", "status": "error",
                  "error": {"code": error.code, "message": str(error)}}
        code = 2
    print(json.dumps(result, ensure_ascii=True, allow_nan=False, separators=(",", ":")))
    return code

