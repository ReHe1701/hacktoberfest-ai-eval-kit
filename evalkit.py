"""Hacktoberfest AI Eval Kit: deterministic checks for saved model responses."""

import argparse
import json
import math
import sys
import unicodedata
from pathlib import Path


class InputError(ValueError):
    """An actionable dataset or prediction error."""


def load_jsonl(path):
    records = []
    seen = set()
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise InputError(f"Cannot read {path}: {exc}") from exc
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError as exc:
            raise InputError(f"{path}:{number}: invalid JSON") from exc
        if not isinstance(record, dict):
            raise InputError(f"{path}:{number}: expected an object")
        identity = record.get("id")
        if not isinstance(identity, str) or not identity.strip():
            raise InputError(f"{path}:{number}: id must be a nonempty string")
        if identity in seen:
            raise InputError(f"{path}:{number}: duplicate id {identity!r}")
        seen.add(identity)
        records.append(record)
    return records


def validate_cases(cases):
    if not cases:
        raise InputError("The case dataset must not be empty")
    for case in cases:
        identity = case["id"]
        for field in ("prompt", "category"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise InputError(f"{identity}: {field} must be a nonempty string")
        check = case.get("check")
        if not isinstance(check, dict):
            raise InputError(f"{identity}: check must be an object")
        kind = check.get("type")
        if kind == "exact":
            if not isinstance(check.get("value"), str):
                raise InputError(f"{identity}: exact requires a string value")
        elif kind in ("contains_all", "json_keys"):
            field = "values" if kind == "contains_all" else "keys"
            values = check.get(field)
            if not isinstance(values, list) or not values or not all(
                isinstance(value, str) and value.strip() for value in values
            ):
                raise InputError(f"{identity}: {kind} requires nonempty string {field}")
        else:
            raise InputError(f"{identity}: unknown check type {kind!r}")


def normalize(text):
    return unicodedata.normalize("NFKC", text).strip().casefold()


def check_response(check, response):
    kind = check["type"]
    if kind == "exact":
        passed = normalize(response) == normalize(check["value"])
        return passed, "Exact match" if passed else "Expected normalized exact match"
    if kind == "contains_all":
        missing = [value for value in check["values"] if normalize(value) not in normalize(response)]
        return not missing, "All required phrases present" if not missing else "Missing phrases: " + ", ".join(missing)
    if kind == "json_keys":
        try:
            value = json.loads(response)
        except ValueError:
            return False, "Response is not JSON"
        if not isinstance(value, dict):
            return False, "Expected a JSON object"
        missing = [key for key in check["keys"] if key not in value]
        return not missing, "Required keys present" if not missing else "Missing keys: " + ", ".join(missing)
    raise InputError(f"Unknown check type {kind!r}")


def evaluate(cases, predictions):
    validate_cases(cases)
    expected = {case["id"] for case in cases}
    responses = {}
    for prediction in predictions:
        identity = prediction["id"]
        if identity not in expected:
            raise InputError(f"Unknown prediction id: {identity}")
        if identity in responses:
            raise InputError(f"Duplicate prediction id: {identity}")
        if not isinstance(prediction.get("response"), str):
            raise InputError(f"{identity}: response must be a string")
        responses[identity] = prediction["response"]
    results = []
    categories = {}
    for case in cases:
        identity = case["id"]
        passed, reason = (False, "Missing response") if identity not in responses else check_response(case["check"], responses[identity])
        results.append({"id": identity, "category": case["category"], "passed": passed, "reason": reason})
        group = categories.setdefault(case["category"], {"passed": 0, "total": 0})
        group["total"] += 1
        group["passed"] += int(passed)
    passed = sum(result["passed"] for result in results)
    return {"passed": passed, "total": len(cases), "pass_rate": passed / len(cases), "categories": categories, "results": results}


def markdown(report):
    def escape(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("\r", " ").replace("\n", " ")
    lines = ["# Hacktoberfest AI Eval Report", "", f"Passed **{report['passed']}/{report['total']}** ({report['pass_rate']:.1%}).", "", "| Case | Category | Result | Detail |", "| --- | --- | --- | --- |"]
    for result in report["results"]:
        cells = [result["id"], result["category"], "PASS" if result["passed"] else "FAIL", result["reason"]]
        lines.append("| " + " | ".join(escape(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def threshold(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number between 0 and 1") from exc
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("must be a finite number between 0 and 1")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="cases.jsonl", help="JSONL evaluation cases")
    parser.add_argument("--predictions", default="answers.jsonl", help="JSONL saved model responses")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path, help="Optional report file; otherwise stdout")
    parser.add_argument("--min-pass-rate", type=threshold, default=1.0)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve() in {Path(args.cases).resolve(), Path(args.predictions).resolve()}:
            raise InputError("Output must not overwrite an input file")
        report = evaluate(load_jsonl(args.cases), load_jsonl(args.predictions))
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else markdown(report)
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (InputError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0 if report["pass_rate"] >= args.min_pass_rate else 1


if __name__ == "__main__":
    sys.exit(main())
