"""Authored library-behavior investigations, not historical bug reproductions."""

CASES = [
    {"id": "compatible-release-prefix", "package": "packaging", "version": "25.0",
     "module": "packaging.specifiers", "variable": "prefix",
     "expectedRepresentations": ["'0!2.2'", "'0!2.2.*'"],
     "upstream": "https://github.com/pypa/packaging/tree/25.0",
     "question": "Why does ~=2.2.0 accept 2.2.5 but reject 2.3.0? Inspect the computed prefix."},
    {"id": "retry-before-cap", "package": "urllib3", "version": "2.5.0",
     "module": "urllib3.util.retry", "variable": "backoff_value",
     "expectedRepresentations": ["2.0"],
     "upstream": "https://github.com/urllib3/urllib3/tree/2.5.0",
     "question": "What backoff was calculated before the one-second maximum was applied?"},
    {"id": "iso-fraction-cursor", "package": "python-dateutil", "version": "2.9.0.post0",
     "module": "dateutil.parser.isoparser", "variable": "pos",
     "expectedRepresentations": ["18", "19"],
     "upstream": "https://github.com/dateutil/dateutil/tree/2.9.0.post0",
     "question": "Where did parsing advance after a nine-digit fractional second and the Z suffix?"},
    {"id": "cli-attached-value", "package": "click", "version": "8.2.1",
     "module": "click.parser", "variable": "explicit_value",
     "expectedRepresentations": ["None", "'bad'"],
     "upstream": "https://github.com/pallets/click/tree/8.2.1",
     "question": "Which attached option value reached the parser before integer validation failed?"},
    {"id": "template-column-remainder", "package": "Jinja2", "version": "3.1.6",
     "module": "jinja2.filters", "variable": "slices_with_extra",
     "expectedRepresentations": ["1"],
     "upstream": "https://github.com/pallets/jinja/tree/3.1.6",
     "question": "Why are ten items divided into column lengths 4, 3, 3? Inspect the remainder."},
    {"id": "chunk-tail-before-fill", "package": "boltons", "version": "25.0.0",
     "module": "boltons.iterutils", "variable": "lc",
     "expectedRepresentations": ["3", "2"],
     "upstream": "https://github.com/mahmoud/boltons/tree/25.0.0",
     "question": "What was the tail length before explicit None padding filled the final chunk?"},
    {"id": "consecutive-group-key", "package": "more-itertools", "version": "10.8.0",
     "module": "more_itertools.more", "variable": "k",
     "expectedRepresentations": ["-1", "-8", "-16"],
     "upstream": "https://github.com/more-itertools/more-itertools/tree/v10.8.0",
     "question": "Which group keys split 1,2,10,11,20 into three consecutive groups?"},
    {"id": "schema-contains-overflow", "package": "jsonschema", "version": "4.25.1",
     "module": "jsonschema._keywords", "variable": "matches",
     "expectedRepresentations": ["0", "1", "2", "3"],
     "upstream": "https://github.com/python-jsonschema/jsonschema/tree/v4.25.1",
     "question": "How many values matched contains when maxContains=2 was exceeded?"},
]


def run(case):
    if case == "compatible-release-prefix":
        from packaging.specifiers import Specifier
        assert list(Specifier("~=2.2.0").filter(["2.2.5", "2.3.0"])) == ["2.2.5"]
    elif case == "retry-before-cap":
        from urllib3.util.retry import RequestHistory, Retry
        history = tuple(RequestHistory("GET", "/", None, 503, None) for _ in range(3))
        retry = Retry(history=history, backoff_factor=0.5, backoff_max=1, backoff_jitter=0)
        assert retry.get_backoff_time() == 1.0
    elif case == "iso-fraction-cursor":
        from dateutil.parser import isoparser
        assert isoparser().parse_isotime("12:34:56.123456789Z").isoformat() == "12:34:56.123456+00:00"
    elif case == "cli-attached-value":
        import click

        @click.command()
        @click.option("--count", type=int)
        def command(count):
            raise AssertionError("invalid input should not reach the callback")

        try:
            command.main(["--count=bad"], standalone_mode=False)
        except click.BadParameter as error:
            assert "valid integer" in str(error)
        else:
            raise AssertionError("expected integer conversion failure")
    elif case == "template-column-remainder":
        from jinja2.filters import sync_do_slice
        assert list(sync_do_slice(list(range(10)), 3)) == [
            [0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]
    elif case == "chunk-tail-before-fill":
        from boltons.iterutils import chunked_iter
        assert list(chunked_iter(range(5), 3, fill=None)) == [[0, 1, 2], [3, 4, None]]
    elif case == "consecutive-group-key":
        from more_itertools import consecutive_groups
        assert [list(group) for group in consecutive_groups([1, 2, 10, 11, 20])] == [
            [1, 2], [10, 11], [20]]
    elif case == "schema-contains-overflow":
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator({
            "contains": {"type": "integer"}, "minContains": 2, "maxContains": 2})
        errors = list(validator.iter_errors([1, "x", 2, 3]))
        assert len(errors) == 1 and errors[0].validator == "maxContains"
    else:
        raise ValueError("unknown compatibility case")


if __name__ == "__main__":
    import sys
    run(sys.argv[1])
