"""A bounded reader for VizTracer 1.1.1's variable and execution-step records.

The two observation streams are intentionally separate. Instant variable
records have timestamps but no assignment lines or reliable call identity.
Function execution steps have call identity and recorded lines, but no
individual timestamps. Merging them would invent ordering information.
"""
from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import stat
from typing import Any

SCHEMA = "aftertrace/1"
MAX_BYTES = 32 * 1024 * 1024
MAX_EVENTS = 200_000
MAX_STEPS = 200_000
MAX_SCALAR_CHARS = 4096
MAX_DISPLAY_CHARS = 256
STEP = re.compile(r"^\((\d+)\) ([A-Za-z_]\w*) = (.*)$", re.DOTALL)
VARIABLE_PREFIX = "Variable Assign - "


class QueryError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def finite_number(value: Any) -> bool:
    return type(value) is int or (type(value) is float and math.isfinite(value))


def strict_json(raw: str | bytes) -> Any:
    def bad_constant(_: str) -> None:
        raise ValueError("non-finite JSON number")

    def unique(pairs: list) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    return json.loads(raw, parse_constant=bad_constant, object_pairs_hook=unique)


def scalar(text: str) -> tuple[bool, Any]:
    """Decode scalar repr syntax, never call eval, repr, or object methods."""
    if len(text) > MAX_SCALAR_CHARS:
        return False, None
    try:
        node = ast.parse(text, mode="eval").body
        if isinstance(node, ast.Constant):
            value = node.value
        elif (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, (ast.UAdd, ast.USub))
            and isinstance(node.operand, ast.Constant)
            and finite_number(node.operand.value)
        ):
            value = node.operand.value
            if isinstance(node.op, ast.USub):
                value = -value
        else:
            return False, None
        if type(value) in (str, bool, type(None)) or finite_number(value):
            return True, value
    except (SyntaxError, ValueError, RecursionError, MemoryError, OverflowError):
        pass
    return False, None


def compare(left: Any, op: str, right: Any) -> bool | None:
    same = type(left) is type(right) or (finite_number(left) and finite_number(right))
    if not same:
        return None
    if op == "eq":
        return left == right
    if op == "ne":
        return left != right
    if op not in {"lt", "le", "gt", "ge"}:
        raise QueryError("invalid_operator", "Use eq, ne, lt, le, gt, or ge.")
    if not ((finite_number(left) and finite_number(right)) or type(left) is str):
        return None
    return {"lt": lambda: left < right, "le": lambda: left <= right,
            "gt": lambda: left > right, "ge": lambda: left >= right}[op]()


def bounded(text: str) -> dict:
    return {"text": text[:MAX_DISPLAY_CHARS],
            "textTruncated": len(text) > MAX_DISPLAY_CHARS,
            "originalCharacters": len(text)}


@dataclass
class Observation:
    id: str
    variable: str
    representation: str
    pid: int | str
    tid: int | str
    timestamp: int | float | None
    call: str | None = None
    recorded_line: int | None = None

    def public(self) -> dict:
        valid, value = scalar(self.representation)
        result = {
            "id": self.id, "variable": self.variable,
            "recordedRepresentation": bounded(self.representation),
            "scalarDecodable": valid,
            "pid": self.pid, "tid": self.tid,
            "timestampUs": self.timestamp, "callId": self.call,
            "recordedLine": self.recorded_line,
        }
        if valid and not (type(value) is str and len(value) > MAX_DISPLAY_CHARS):
            result["scalarValue"] = value
        return result


class Trace:
    def __init__(self, path: str | Path):
        path = Path(path)
        try:
            info = path.stat()
            if not stat.S_ISREG(info.st_mode):
                raise QueryError("invalid_file", "A regular JSON file is required.")
            if info.st_size > MAX_BYTES:
                raise QueryError("input_too_large", "Input exceeds the 32 MiB query limit.")
            with path.open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise QueryError("input_too_large", "Input exceeds the 32 MiB query limit.")
            data = strict_json(raw)
        except (OSError, ValueError, RecursionError) as error:
            if isinstance(error, QueryError):
                raise
            raise QueryError("invalid_trace", "Cannot read a valid, bounded JSON trace.") from error
        if not isinstance(data, dict) or not isinstance(data.get("traceEvents"), list):
            raise QueryError("invalid_trace", "Expected a VizTracer object with traceEvents.")
        self.trace_id = hashlib.sha256(raw).hexdigest()
        self.bytes = len(raw)
        self.metadata = data.get("viztracer_metadata", {})
        if not isinstance(self.metadata, dict):
            raise QueryError("invalid_metadata", "viztracer_metadata must be an object.")
        self.overflow = self.metadata.get("overflow")
        if self.overflow is not None and type(self.overflow) is not bool:
            raise QueryError("invalid_metadata", "overflow must be a boolean when present.")
        self.version = self.metadata.get("version")
        if self.version not in (None, "1.1.1"):
            raise QueryError("unsupported_version", "This alpha supports VizTracer 1.1.1 only.")
        events = data["traceEvents"]
        if len(events) > MAX_EVENTS:
            raise QueryError("too_many_events", "Input exceeds 200000 events.")
        self.event_count = len(events)
        self.variables: list[Observation] = []
        self.calls: dict[str, dict] = {}
        self.steps: dict[str, list[Observation]] = {}
        self.malformed = 0
        self.step_count = 0
        self._data = data
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                raise QueryError("invalid_event", "Every trace event must be an object.")
            name, phase = event.get("name"), event.get("ph")
            if not isinstance(name, str):
                continue
            if phase == "i" and name.startswith(VARIABLE_PREFIX):
                parts = name[len(VARIABLE_PREFIX):].split(" = ", 1)
                if len(parts) != 2 or not parts[0].isidentifier() or len(parts[0]) > 128:
                    self.malformed += 1
                    continue
                pid, tid, timestamp = self._position(event)
                self.variables.append(Observation(f"v{index}", *parts, pid, tid, timestamp))
            if phase == "X":
                pid, tid, timestamp = self._position(event)
                duration = event.get("dur")
                if not finite_number(duration) or duration < 0:
                    raise QueryError("invalid_event", "A complete event needs a non-negative duration.")
                call_id = f"c{index}"
                args = event.get("args", {})
                if not isinstance(args, dict):
                    raise QueryError("invalid_event", "Event args must be an object.")
                values = args.get("exec_steps", [])
                if not isinstance(values, list):
                    raise QueryError("invalid_steps", "exec_steps must be an array.")
                self.step_count += len(values)
                if self.step_count > MAX_STEPS:
                    raise QueryError("too_many_steps", "Input exceeds 200000 execution steps.")
                self.calls[call_id] = {
                    "id": call_id, "name": name, "pid": pid, "tid": tid,
                    "timestampUs": timestamp, "durationUs": duration,
                    "recordedSteps": len(values),
                }
                self.steps[call_id] = []
                for step_index, text in enumerate(values):
                    match = STEP.fullmatch(text) if isinstance(text, str) else None
                    if not match:
                        self.malformed += 1
                        continue
                    line, variable, representation = match.groups()
                    if len(line) > 10 or len(variable) > 128:
                        self.malformed += 1
                        continue
                    self.steps[call_id].append(Observation(
                        f"{call_id}:s{step_index}", variable, representation,
                        pid, tid, None, call_id, int(line)))
        # Tie order is file order, not a claim about sub-timestamp execution.
        self.variables.sort(key=lambda event: event.timestamp)

    @staticmethod
    def _position(event: dict) -> tuple:
        pid, tid, timestamp = event.get("pid"), event.get("tid"), event.get("ts")
        if (type(pid) not in (str, int) or type(tid) not in (str, int)
                or not finite_number(timestamp)):
            raise QueryError("invalid_event", "Recorded observations need pid, tid and a finite ts.")
        if len(str(pid)) > 128 or len(str(tid)) > 128:
            raise QueryError("invalid_event", "Process and thread IDs exceed the query limit.")
        return pid, tid, timestamp

    def envelope(self, status: str, stream: str = "variable_instants") -> dict:
        return {
            "schema": SCHEMA, "traceId": self.trace_id, "status": status,
            "stream": stream,
            "coverage": {
                "bufferOverflow": self.overflow,
                "captureCompleteness": "unknown",
                "malformedObservations": self.malformed,
                "valueFidelity": "recorded_repr_not_runtime_type",
                "order": ("within_call_recorded_steps" if stream == "function_steps"
                          else "timestamp_then_file_order_not_causal"),
            },
        }

    def select(self, variable: str, call: str | None = None,
               pid: str | None = None, tid: str | None = None) -> list[Observation]:
        if call is not None and call not in self.calls:
            raise QueryError("unknown_call", "Call ID is absent from this trace.")
        source = self.variables if call is None else self.steps[call]
        return [event for event in source if event.variable == variable
                and (pid is None or str(event.pid) == pid)
                and (tid is None or str(event.tid) == tid)]

    def inspect(self) -> dict:
        result = self.envelope("ok")
        names = Counter(event.variable for event in self.variables)
        step_names = Counter(event.variable for values in self.steps.values() for event in values)
        result.update({
            "inputBytes": self.bytes, "viztracerVersion": self.version,
            "events": self.event_count, "calls": len(self.calls),
            "variableObservations": len(self.variables),
            "functionStepObservations": sum(map(len, self.steps.values())),
            "variables": dict(sorted(names.items())[:100]),
            "stepVariables": dict(sorted(step_names.items())[:100]),
            "variableNamesTruncated": len(names) > 100 or len(step_names) > 100,
        })
        return result

    def list_calls(self, function: str | None, offset: int, limit: int) -> dict:
        calls = [call for call in self.calls.values()
                 if function is None or call["name"].split(" (", 1)[0] == function]
        result = self.envelope("ok", "function_steps")
        result.update({"total": len(calls), "offset": offset,
                       "nextOffset": offset + limit if len(calls) > offset + limit else None,
                       "calls": [{**call, "name": bounded(call["name"])}
                                 for call in calls[offset:offset + limit]]})
        return result

    def history(self, variable: str, call: str | None, pid: str | None,
                tid: str | None, offset: int, limit: int) -> tuple[dict, int]:
        observations = self.select(variable, call, pid, tid)
        result = self.envelope("ok" if observations else "not_recorded",
                               "function_steps" if call else "variable_instants")
        result.update({"total": len(observations), "offset": offset,
                       "nextOffset": offset + limit if len(observations) > offset + limit else None,
                       "observations": [o.public() for o in observations[offset:offset + limit]]})
        return result, 0 if observations else 3

    def first(self, variable: str, op: str, value: Any, call: str | None,
              pid: str | None, tid: str | None) -> tuple[dict, int]:
        observations = self.select(variable, call, pid, tid)
        result = self.envelope("not_recorded", "function_steps" if call else "variable_instants")
        if not observations:
            return result, 3
        streams = {(type(o.pid), o.pid, type(o.tid), o.tid) for o in observations}
        if len(streams) > 1:
            result.update({"status": "ambiguous_stream", "hint": "Filter with --pid and --tid, or --call."})
            return result, 3
        unsupported = 0
        for observation in observations:
            valid, left = scalar(observation.representation)
            matches = compare(left, op, value) if valid else None
            if matches is None:
                unsupported += 1
            elif matches:
                same_time = (sum(o.timestamp == observation.timestamp for o in observations)
                             if call is None else 1)
                partial = unsupported > 0 or same_time > 1 or self.malformed > 0
                result.update({
                    "status": "partial_match" if partial else "found",
                    "match": observation.public(),
                    "earlierUncomparableObservations": unsupported,
                    "sameTimestampObservations": same_time,
                    "claim": "first_comparable_recorded_match_in_selected_stream",
                    "rootCauseEstablished": False,
                })
                return result, 3 if partial else 0
        incomplete = unsupported > 0 or self.overflow is not False or self.malformed > 0
        result.update({"status": "inconclusive" if incomplete else "no_observed_match",
                       "uncomparableObservations": unsupported,
                       "claim": "only_the_selected_recorded_observations_were_checked"})
        return result, 3 if incomplete else 1
