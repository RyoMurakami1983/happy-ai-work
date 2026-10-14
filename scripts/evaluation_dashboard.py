#!/usr/bin/env python3
"""Validate a sanitized local dashboard export; never run or certify an evaluation."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

if __package__:
    from . import validate_evals
else:
    import validate_evals


OUTCOMES = ("pass", "fail", "hard_fail", "incomplete", "indeterminate", "not_run")
GATES = ("quality", "safety", "permission", "critical")
METRICS = ("raw_burden", "dependency_delay", "rework", "human_review_time")


def eligible(case: dict, run: dict, method: dict) -> bool:
    """Declared eligibility only; this is not authentication of source evidence."""
    details = case["burden_details"]
    return (
        case["outcome"] == "pass" and case["completion"] == "complete"
        and all(case["gates"][gate] == "pass" for gate in GATES)
        and run["evaluation_mode"] == "A" and case["independence"] == "valid"
        and case["contamination"] == "clean" and case["trace"] == "sufficient"
        and bool(case["evidence"]) and method["locked"]
        and method["preregistration"]["locked_at"] <= run["started_at"]
        and case["q"] is not None and case["b"] is not None
        and details["accounting"] == "deduplicated"
        and all(details[key]["value"] is not None for key in METRICS)
        and (case["b"] == 0 or bool(details["event_links"]))
    )


def cohort_key(run: dict, method: dict, data_kind: str) -> str:
    provenance = {key: value for key, value in run["provenance"].items() if key != "implementation_revision"}
    for key in ("tools", "sources"):
        provenance[key] = sorted(provenance[key], key=lambda item: item["id"])
    components = [data_kind, run["condition_id"], run["condition_sha256"], run["evaluation_mode"],
                  method, provenance, sorted([case["case_id"], case["family"]] for case in run["cases"])]
    return json.dumps(components, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def summarize(payload: dict, family: str | None = None) -> dict:
    methods = {method["id"]: method for method in payload["methods"]}
    rows = []
    for run in payload["runs"]:
        method = methods[run["method_id"]]
        cases = [case for case in run["cases"] if family is None or case["family"] == family]
        quality = [case["q"] for case in cases if case["q"] is not None]
        burden = [case["b"] for case in cases if case["b"] is not None]
        scores = [case["q"] / (1 + method["lambda"] * case["b"])
                  for case in cases if eligible(case, run, method)]
        counts = {key: sum(case["outcome"] == key for case in cases) for key in OUTCOMES}
        rows.append({
            "id": run["id"], "cohort": cohort_key(run, method, payload["data_kind"]),
            "iteration": run["iteration"], "evaluated_at": run["evaluated_at"],
            "assigned": len(cases), "counts": counts,
            "rate": 100 * counts["pass"] / len(cases) if cases else None,
            "q": sum(quality) / len(quality) if quality else None,
            "b": sum(burden) / len(burden) if burden else None,
            "s": sum(scores) / len(scores) if scores else None,
            "q_count": len(quality), "b_count": len(burden), "s_count": len(scores),
            "burden_basis": method["burden_basis"],
        })
    return {"schema_version": 1, "data_kind": payload["data_kind"], "runs": rows}


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "evals" / "schema" / "dashboard-export.v1.schema.json"
MAX_BYTES = 5 * 1024 * 1024


class ValidationError(ValueError):
    """An invalid import never changes the caller's current data."""


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON property")
        result[key] = value
    return result


def reject_constant(_value: str) -> None:
    raise ValidationError("nonfinite JSON number")


def validate_schema(value: object, node: dict, schema: dict, path: str, failures: list[str], depth: int = 0) -> None:
    if depth > 80:
        failures.append(f"{path}: input exceeds maximum depth")
        return
    if "$ref" in node:
        node = schema["$defs"][node["$ref"].split("/")[-1]]
    if "anyOf" in node:
        choices = [branch for branch in node["anyOf"] if validate_evals.matches_type(value, branch["type"])]
        if not choices:
            failures.append(f"{path}: invalid nullable value type")
            return
        node = choices[0]
    # JSON Schema integers are mathematical integers, including JSON spelling 1.0.
    if node.get("type") == "integer" and isinstance(value, float) and math.isfinite(value) and value.is_integer():
        value = int(value)
    # Reuse the repository contract for types, keys, required fields, enums, patterns and unique arrays.
    shallow = {key: child for key, child in node.items() if key not in {"properties", "items"}}
    if "properties" in node:
        shallow["properties"] = dict.fromkeys(node["properties"], {})
    validate_evals.validate_against_schema(value, shallow, location=path, failures=failures)
    if not validate_evals.matches_type(value, node.get("type", "")):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            failures.append(f"{path}: number must be finite")
        elif (value < node.get("minimum", 0) or value > node.get("maximum", 1000000)
              or ("exclusiveMinimum" in node and value <= node["exclusiveMinimum"])):
            failures.append(f"{path}: number outside bounds")
    elif isinstance(value, str):
        if len(value) > node.get("maxLength", 500):
            failures.append(f"{path}: string is too long")
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            failures.append(f"{path}: invalid Unicode surrogate")
        if node.get("format") == "date-time":
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                failures.append(f"{path}: invalid UTC timestamp")
    elif isinstance(value, list):
        if len(value) > node.get("maxItems", 5000):
            failures.append(f"{path}: too many items")
        for index, child in enumerate(value):
            validate_schema(child, node["items"], schema, f"{path}[{index}]", failures, depth + 1)
    elif isinstance(value, dict):
        for key, child in value.items():
            if key in node["properties"]:
                validate_schema(child, node["properties"][key], schema, f"{path}.{key}", failures, depth + 1)


def unique_ids(items: list[dict], path: str, failures: list[str], key: str = "id") -> None:
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        failures.append(f"{path}: duplicate {key}")


def expected_outcome(case: dict, mode: str) -> str:
    gates = case["gates"]
    if any(gates[key] == "fail" for key in ("safety", "permission", "critical")):
        return "hard_fail"
    if case["completion"] == "not_run":
        return "not_run"
    if case["completion"] == "incomplete":
        return "incomplete"
    if mode != "A":
        return "indeterminate"
    if gates["quality"] == "fail":
        return "fail"
    return "pass" if all(value == "pass" for value in gates.values()) else "indeterminate"


def validate(payload: object) -> dict:
    """Validate structure and cross-field constraints without verifying private evidence."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    validate_schema(payload, schema, schema, "export", failures)
    if failures:
        raise ValidationError("\n".join(failures[:20]))
    # The schema establishes object shape before semantic indexing.
    assert isinstance(payload, dict)
    validate_evals.walk_fields(payload, path=Path("dashboard-import.json"), failures=failures)
    if validate_evals.SECRET_RE.search(json.dumps(payload, ensure_ascii=False)):
        failures.append("export: possible secret; sanitized summaries only")
    unique_ids(payload["methods"], "methods", failures)
    unique_ids(payload["runs"], "runs", failures)
    methods = {method["id"]: method for method in payload["methods"]}
    for method in payload["methods"]:
        if method["locked"]:
            if method["preregistration"] is None or method["lambda"] is None or method["beta"] is None:
                failures.append("method: locked method requires registration and explicit coefficients")
        elif method["preregistration"] is not None:
            failures.append("method: draft method cannot declare a locked registration")
    observations: set[str] = set()
    iterations: set[tuple[str, int]] = set()
    dates: set[tuple[str, str]] = set()
    for run in payload["runs"]:
        method = methods.get(run["method_id"])
        if method is None:
            failures.append("run: unknown method_id")
            continue
        if not run["started_at"] <= run["evaluated_at"] <= payload["generated_at"]:
            failures.append("run: inconsistent timestamp ordering")
        registration = method["preregistration"]
        if registration is not None and registration["locked_at"] > run["started_at"]:
            failures.append("run: preregistration must precede run start")
        provenance = run["provenance"]
        for key in ("tools", "sources"):
            unique_ids(provenance[key], f"provenance.{key}", failures)
        unique_ids(run["cases"], "cases", failures, "case_id")
        if set(run["assigned_case_ids"]) != {case["case_id"] for case in run["cases"]}:
            failures.append("run: assigned_case_ids must match all case observations")
        key = cohort_key(run, method, payload["data_kind"])
        if (key, run["iteration"]) in iterations or (key, run["evaluated_at"]) in dates:
            failures.append("run: duplicate cohort iteration or evaluation time")
        iterations.add((key, run["iteration"]))
        dates.add((key, run["evaluated_at"]))
        for case in run["cases"]:
            if case["id"] in observations:
                failures.append("case: duplicate observation id")
            observations.add(case["id"])
            if case["completion"] == "not_run" and (
                any(value != "not_evaluated" for value in case["gates"].values())
                or case["q"] is not None or case["b"] is not None
            ):
                failures.append("case: not_run requires unevaluated gates and null Q/B")
            if case["outcome"] != expected_outcome(case, run["evaluation_mode"]):
                failures.append("case: outcome contradicts completion, gates or evaluation mode")
            for metric in ("q", "b"):
                if case[metric] is not None and case[metric] > method[f"{metric}_max"]:
                    failures.append(f"case: {metric} exceeds method scale")
            expected_basis = "unavailable" if case["b"] is None else method["burden_basis"]
            if case["burden_basis"] != expected_basis:
                failures.append("case: burden basis contradicts method or missingness")
            if case["trace"] == "sufficient" and not case["evidence"]:
                failures.append("case: sufficient trace requires evidence references")
            unique_ids(case["evidence"], "evidence", failures)
            details = case["burden_details"]
            unique_ids(details["event_links"], "event_links", failures, "decision_event_id")
            for metric in METRICS:
                observation = details[metric]
                if (observation["value"] is None) != (observation["basis"] == "unavailable"):
                    failures.append("case: metric basis contradicts missingness")
    if failures:
        raise ValidationError("\n".join(failures[:20]))
    return payload


def loads(text: str) -> dict:
    try:
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ValidationError("input exceeds 5 MiB")
        payload = json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
        return validate(payload)
    except ValidationError:
        raise
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise ValidationError("invalid UTF-8 JSON input") from exc


def load(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise ValidationError("input exceeds 5 MiB")
    return loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--summary", type=Path, help="Create a new summary; existing paths are never overwritten.")
    args = parser.parse_args()
    try:
        payload = load(args.input)
    except (OSError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    summary = summarize(payload)
    if args.summary:
        try:
            # Exclusive creation also refuses input aliases, symlinks and hardlinks without a check/write race.
            with args.summary.open("x", encoding="utf-8") as output:
                output.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        except OSError as exc:
            print(f"Could not create new summary (existing files are preserved): {exc}", file=sys.stderr)
            return 1
    print("VALID: local summary only; source authenticity is not verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
