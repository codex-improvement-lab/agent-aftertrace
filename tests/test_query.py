import json
from pathlib import Path
import subprocess
import sys

import pytest

from aftertrace.cli import main
from aftertrace.query import MAX_BYTES, QueryError, Trace, compare, scalar


def instant(value, ts=1, variable="balance", pid=1, tid=1):
    return {"ph": "i", "name": f"Variable Assign - {variable} = {value}",
            "ts": ts, "pid": pid, "tid": tid}


def complete(steps, name="settle (example.py:1)", ts=0):
    return {"ph": "X", "name": name, "ts": ts, "dur": 10, "pid": 1, "tid": 1,
            "args": {"exec_steps": steps}}


def save(tmp_path, events, overflow=False):
    path = tmp_path / "recording.json"
    path.write_text(json.dumps({"traceEvents": events,
                               "viztracer_metadata": {"overflow": overflow, "version": "1.1.1"}}),
                    encoding="utf-8")
    return path


@pytest.mark.parametrize("raw,value", [
    ("-33", -33), ("+2.5", 2.5), ("False", False), ("None", None),
    (r"'a\nb'", "a\nb"), ("'🔎'", "🔎"),
])
def test_decode_scalar_syntax(raw, value):
    assert scalar(raw) == (True, value)


@pytest.mark.parametrize("raw", [
    "__import__('os').system('echo unsafe')", "[1,2]", "{'x': 1}", "nan",
    "float('inf')", "1e999", "'x' * 999999", "-True", "(lambda: 1)()", "b'bytes'",
    "9" * 5000, "[" * 1000,
])
def test_no_execution_or_complex_decoding(raw):
    assert scalar(raw) == (False, None)


def test_query_is_read_only_and_returns_earlier_value(tmp_path):
    path = save(tmp_path, [instant(20, 1), instant(-33, 2), instant(71, 3)])
    original = path.read_bytes()
    trace = Trace(path)
    result, code = trace.first("balance", "lt", 0, None, None, None)
    assert code == 0
    assert result["match"]["scalarValue"] == -33
    assert result["match"]["recordedLine"] is None
    assert result["match"]["callId"] is None
    assert result["rootCauseEstablished"] is False
    assert result["coverage"]["captureCompleteness"] == "unknown"
    assert path.read_bytes() == original
    assert Trace(path).trace_id == trace.trace_id


def test_call_steps_do_not_invent_timestamps_or_merge_instants(tmp_path):
    path = save(tmp_path, [instant(-99), complete(["(2) balance = 20", "(8) balance = -33"]),
                           complete(["(2) balance = 50"], ts=12)])
    trace = Trace(path)
    result, code = trace.first("balance", "lt", 0, "c1", None, None)
    assert code == 0
    assert result["match"]["scalarValue"] == -33
    assert result["match"]["recordedLine"] == 8
    assert result["match"]["timestampUs"] is None
    assert result["match"]["id"] == "c1:s1"
    assert trace.history("balance", "c2", None, None, 0, 20)[0]["total"] == 1
    assert trace.first("balance", "lt", 0, "c2", None, None)[1] == 1


@pytest.mark.parametrize("overflow", [None, True])
def test_no_match_is_inconclusive_if_buffer_extent_unknown_or_lost(tmp_path, overflow):
    result, code = Trace(save(tmp_path, [instant(20)], overflow)).first(
        "balance", "lt", 0, None, None, None)
    assert code == 3
    assert result["status"] == "inconclusive"


def test_observed_match_does_not_hide_overflow(tmp_path):
    result, code = Trace(save(tmp_path, [instant(-33)], True)).first(
        "balance", "lt", 0, None, None, None)
    assert code == 0
    assert result["coverage"]["bufferOverflow"] is True
    assert "recorded_match" in result["claim"]


def test_absent_variable_is_not_a_negative_predicate(tmp_path):
    result, code = Trace(save(tmp_path, [instant(20)])).first("never_captured", "eq", 0, None, None, None)
    assert code == 3
    assert result["status"] == "not_recorded"


def test_unsupported_value_before_match_prevents_first_claim(tmp_path):
    trace = Trace(save(tmp_path, [instant("<Opaque object>", 1), instant(-33, 2)]))
    result, code = trace.first("balance", "lt", 0, None, None, None)
    assert code == 3
    assert result["status"] == "partial_match"
    assert result["earlierUncomparableObservations"] == 1


def test_type_mismatch_is_unknown_not_python_bool_integer_coercion(tmp_path):
    assert compare(False, "eq", 0) is None
    assert compare(0, "eq", 0.0) is True
    result, code = Trace(save(tmp_path, [instant("False")])).first(
        "balance", "eq", 0, None, None, None)
    assert (result["status"], code) == ("inconclusive", 3)


def test_concurrent_streams_require_explicit_filter(tmp_path):
    trace = Trace(save(tmp_path, [instant(-33, tid=1), instant(-99, ts=2, tid=2)]))
    result, code = trace.first("balance", "lt", 0, None, None, None)
    assert (result["status"], code) == ("ambiguous_stream", 3)
    result, code = trace.first("balance", "lt", 0, None, "1", "2")
    assert code == 0 and result["match"]["scalarValue"] == -99


def test_timestamp_tie_does_not_claim_execution_order(tmp_path):
    trace = Trace(save(tmp_path, [instant(-33), instant(-99)]))
    result, code = trace.first("balance", "lt", 0, None, None, None)
    assert code == 3 and result["sameTimestampObservations"] == 2


def test_pagination_and_display_bounds(tmp_path):
    path = save(tmp_path, [instant(repr("x" * 600), ts=i) for i in range(30)])
    trace = Trace(path)
    first, code = trace.history("balance", None, None, None, 0, 20)
    second, _ = trace.history("balance", None, None, None, first["nextOffset"], 20)
    assert code == 0
    assert len(first["observations"]) == 20
    assert len(second["observations"]) == 10
    row = first["observations"][0]
    assert row["recordedRepresentation"]["textTruncated"] is True
    assert len(row["recordedRepresentation"]["text"]) == 256
    assert "scalarValue" not in row
    assert second["nextOffset"] is None


def test_malformed_steps_are_reported(tmp_path):
    trace = Trace(save(tmp_path, [complete(["unknown format", "(8) balance = -33"])]))
    result, code = trace.first("balance", "lt", 0, "c0", None, None)
    assert result["coverage"]["malformedObservations"] == 1
    assert code == 3


@pytest.mark.parametrize("raw", [
    "{}", "[]", '{"traceEvents":1}', '{"traceEvents":[null]}',
    '{"traceEvents":[],"traceEvents":[]}', '{"traceEvents":[],"bad":NaN}',
    '{"traceEvents":[],"viztracer_metadata":{"version":"9.9.9"}}',
    '{"traceEvents":[],"viztracer_metadata":{"overflow":"false"}}',
])
def test_invalid_input_fails_closed(tmp_path, raw):
    path = tmp_path / "input.json"
    path.write_text(raw)
    with pytest.raises(QueryError):
        Trace(path)


def test_input_budget_before_parsing(tmp_path):
    path = tmp_path / "large.json"
    with path.open("wb") as file:
        file.truncate(MAX_BYTES + 1)
    with pytest.raises(QueryError, match="32 MiB"):
        Trace(path)


def test_target_code_in_recording_is_not_executed(tmp_path):
    marker = tmp_path / "should-not-exist"
    payload = f"__import__('pathlib').Path({str(marker)!r}).touch()"
    path = save(tmp_path, [instant(payload)])
    result, code = Trace(path).first("balance", "eq", 1, None, None, None)
    assert code == 3 and not marker.exists()


def test_actual_cli_exit_codes_and_json(tmp_path):
    path = save(tmp_path, [instant(-33)])
    for variable, operator, value, expected in [
        ("balance", "lt", "0", 0),
        ("balance", "gt", "0", 1),
        ("absent", "eq", "0", 3),
        ("balance", "eq", "__import__('os')", 2),
    ]:
        process = subprocess.run([sys.executable, "-m", "aftertrace", "first", str(path),
                                  "--var", variable, "--op", operator, "--value", value],
                                 capture_output=True, text=True)
        assert process.returncode == expected, process.stderr
        assert json.loads(process.stdout)["schema"] == "aftertrace/1"
        assert process.stderr == ""


@pytest.mark.parametrize("arguments", [
    [], ["wrong"], ["inspect", "absent.json"],
    ["history", "any.json", "--var", "a", "--limit", "101"],
    ["history", "any.json", "--var", "a", "--offset", "-1"],
    ["first", "any.json", "--var", "a", "--op", "eq", "--value", "[1]"],
    ["first", "any.json", "--var", "a", "--op", "eq", "--value", "1e999"],
    ["first", "any.json", "--var", "a.b", "--op", "eq", "--value", "0"],
])
def test_cli_errors_are_json(arguments, capsys):
    assert main(arguments) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_unknown_call_does_not_fall_back_to_global_history(tmp_path):
    trace = Trace(save(tmp_path, [instant(-33)]))
    with pytest.raises(QueryError, match="Call ID"):
        trace.first("balance", "lt", 0, "c999", None, None)

