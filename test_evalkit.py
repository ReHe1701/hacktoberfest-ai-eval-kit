"""Regression tests for validation, scoring, reports and CLI exit codes."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import evalkit


ROOT = Path(__file__).resolve().parent


class EvalTests(unittest.TestCase):
    def setUp(self):
        self.cases = evalkit.load_jsonl(ROOT / "cases.jsonl")
        self.answers = evalkit.load_jsonl(ROOT / "answers.jsonl")

    def test_demo_passes(self):
        report = evalkit.evaluate(self.cases, self.answers)
        self.assertEqual(report["pass_rate"], 1)
        self.assertEqual(report["total"], len(self.cases))
        self.assertEqual(sum(group["total"] for group in report["categories"].values()), report["total"])

    def test_unicode_exact(self):
        self.assertTrue(evalkit.check_response({"type": "exact", "value": "Hacktoberfest"}, "  ＨＡＣＫＴＯＢＥＲＦＥＳＴ\n")[0])

    def test_wrong_exact(self):
        self.assertFalse(evalkit.check_response({"type": "exact", "value": "42"}, "The answer is 42")[0])

    def test_contains_requires_every_phrase(self):
        self.assertFalse(evalkit.check_response({"type": "contains_all", "values": ["tests", "docs"]}, "Run tests")[0])

    def test_json_keys_are_case_sensitive(self):
        self.assertFalse(evalkit.check_response({"type": "json_keys", "keys": ["name"]}, '{"Name":"x"}')[0])

    def test_json_invalid_and_nonobjects_fail(self):
        for response in ("bad json", "[]", "null", '"text"', "```json\n{}\n```", "{}"):
            with self.subTest(response=response):
                self.assertFalse(evalkit.check_response({"type": "json_keys", "keys": ["title"]}, response)[0])

    def test_missing_response_counts_in_total(self):
        report = evalkit.evaluate(self.cases, self.answers[:-1])
        self.assertEqual(report["total"], len(self.cases))
        self.assertEqual(report["passed"], len(self.cases) - 1)
        self.assertEqual(report["results"][-1]["reason"], "Missing response")

    def test_empty_predictions_score_zero(self):
        self.assertEqual(evalkit.evaluate(self.cases, [])["pass_rate"], 0)

    def test_unknown_prediction_rejected(self):
        with self.assertRaises(evalkit.InputError):
            evalkit.evaluate(self.cases, [{"id": "unknown", "response": "x"}])

    def test_wrong_response_type_rejected(self):
        with self.assertRaises(evalkit.InputError):
            evalkit.evaluate(self.cases, [{"id": self.cases[0]["id"], "response": 42}])

    def test_invalid_checks_rejected(self):
        for check in ({"type": "unknown"}, {"type": "exact", "value": 1}, {"type": "contains_all", "values": []}, {"type": "json_keys", "keys": [""]}, None):
            with self.subTest(check=check):
                cases = copy.deepcopy(self.cases)
                cases[0]["check"] = check
                with self.assertRaises(evalkit.InputError):
                    evalkit.evaluate(cases, [])

    def test_empty_dataset_rejected(self):
        with self.assertRaises(evalkit.InputError):
            evalkit.evaluate([], [])

    def test_markdown_escapes_table_content(self):
        report = {"passed": 0, "total": 1, "pass_rate": 0, "results": [{"id": "a|b\nc", "category": "<tag>", "passed": False, "reason": "missing"}]}
        rendered = evalkit.markdown(report)
        self.assertIn("a&#124;b c", rendered)
        self.assertIn("&lt;tag&gt;", rendered)

    def test_jsonl_validation(self):
        for content in ('{"id":"x"}\n{"id":"x"}', '{bad}', '[]', '{"id":0}', '{"id":" "}'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "data.jsonl"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(evalkit.InputError):
                    evalkit.load_jsonl(path)

    def test_blank_lines_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.jsonl"
            path.write_text('\n {"id":"x"}\n\n', encoding="utf-8")
            self.assertEqual(evalkit.load_jsonl(path), [{"id": "x"}])

    def run_cli(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            code = evalkit.main(["--cases", str(ROOT / "cases.jsonl"), "--predictions", str(ROOT / "answers.jsonl"), *extra])
        return code, out.getvalue(), err.getvalue()

    def test_cli_json_success(self):
        code, out, err = self.run_cli("--format", "json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["pass_rate"], 1)
        self.assertEqual(err, "")

    def test_cli_failed_evaluation_and_threshold(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.jsonl"
            path.write_text("", encoding="utf-8")
            self.assertEqual(self.run_cli("--predictions", str(path))[0], 1)
            self.assertEqual(self.run_cli("--predictions", str(path), "--min-pass-rate", "0")[0], 0)

    def test_cli_io_error(self):
        with tempfile.TemporaryDirectory() as folder:
            code, _, err = self.run_cli("--cases", str(Path(folder) / "missing"))
            self.assertEqual(code, 2)
            self.assertIn("Cannot read", err)

    def test_cli_output_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.md"
            self.assertEqual(self.run_cli("--output", str(path))[0], 0)
            self.assertIn("100.0%", path.read_text(encoding="utf-8"))
            self.assertEqual(self.run_cli("--output", str(ROOT / "cases.jsonl"))[0], 2)

    def test_invalid_threshold(self):
        for value in ("nan", "inf", "-0.1", "1.1", "oops"):
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                evalkit.main(["--min-pass-rate", value])
            self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
