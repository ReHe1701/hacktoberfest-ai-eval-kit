# 🎃 Hacktoberfest AI Eval Kit

**Small checks. Clear evidence. Better open-source AI.**

A beginner-friendly, zero-dependency Python toolkit for checking saved AI responses against a small bilingual dataset. Built for learning and contributing during **Hacktoberfest 2026** and beyond.

**中文：** 一个面向 Hacktoberfest 的开源 AI 回答评测工具。无需 API Key、无需安装依赖，使用中英文样例学习如何编写评测用例、发现失败结果并改进工具。

## Quick start / 快速开始

Requires Python 3.9 or newer. Clone or download this repository, then run from its root:

```sh
python3 evalkit.py
python3 -m unittest discover -v
python3 evalkit.py --format json --output report.json
```

The included **handwritten demo responses** pass all six checks. They are fixtures, not measured results from a real model.

```text
Passed 6/6 (100.0%).
```

## Evaluate your own model

1. Read each `prompt` in `cases.jsonl` and run it through the model of your choice.
2. Save one JSON object per line in `my-answers.jsonl`, matching case IDs:
   `{"id":"arithmetic","response":"42"}`
3. Run the evaluator:

```sh
python3 evalkit.py --predictions my-answers.jsonl --min-pass-rate 0.8
python3 evalkit.py --predictions my-answers.jsonl --format markdown --output report.md
```

The tool reads local files only. It makes no network calls, executes no model-generated code, and does not download or run a model. You choose how to generate predictions, including using an open-weight model locally. Do not commit private prompts, credentials, or personal data.

## Checks and data contract

Each case needs a unique nonempty string `id`, a `prompt`, a `category`, and a `check` object. Prediction records require `id` and string `response`. Blank lines are ignored; duplicate IDs and unknown prediction IDs are input errors. Missing predictions are failures and remain in the denominator. An empty prediction file therefore scores zero.

| Type | Check object | Behavior |
| --- | --- | --- |
| Exact answer | `{"type":"exact","value":"42"}` | Compare after Unicode NFKC normalization, trimming outer whitespace and case folding |
| Required phrases | `{"type":"contains_all","values":["tests","documentation"]}` | All normalized substrings must occur; this is not word or semantic matching |
| JSON shape | `{"type":"json_keys","keys":["title","steps"]}` | Response must parse as a JSON object containing these case-sensitive top-level keys |

`json_keys` does not validate value types or nested schemas. Markdown code fences around JSON fail this check. Reports include per-case reasons and JSON reports include counts per category. This tiny educational dataset is **not a model-quality benchmark**: keyword checks can pass incorrect answers and fail valid paraphrases. Review outputs manually and report limitations with any comparison.

| Exit code | Meaning |
| --- | --- |
| `0` | Pass rate meets the threshold (default `1.0`) |
| `1` | Valid evaluation, but pass rate is below the threshold |
| `2` | Invalid input, arguments or file access |

`--min-pass-rate` accepts finite values from 0 to 1 inclusive. `--output` must not point at an input file. Run `python3 evalkit.py --help` for all options.

## Hacktoberfest / 参与贡献

We welcome useful contributions: better bilingual cases, reproducible bug reports, new well-tested checks and clearer learning material. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [Hacktoberfest guide](HACKTOBERFEST.md).

The [official 2026 FAQ](https://hacktoberfest.com/questions) describes a focus on community events and open-source AI learning; PR/MR counts no longer earn Hacktoberfest rewards. This is an independent community project, not an official event or a promise of eligibility or prizes. Check the official site for current participation requirements.

## Project map

- `evalkit.py` — CLI, validation and three deterministic evaluators
- `cases.jsonl` — six bilingual learning cases
- `answers.jsonl` — handwritten passing fixtures
- `test_evalkit.py` — unit and CLI integration tests
- `CONTRIBUTING.md` — contribution workflow and acceptance criteria
- `HACKTOBERFEST.md` — October workshop plan and starter tasks

## License

MIT. Original sample data is covered by the same license. See [LICENSE](LICENSE).
