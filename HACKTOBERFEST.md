# 🎃 Build, evaluate, contribute — Hacktoberfest 2026

This independent project is a hands-on activity for people learning about open-source AI. Our theme: **make AI evaluation understandable, reproducible and open to everyone**.

## A 45-minute workshop

1. **0–10 min:** Run the six demo cases and inspect their checks.
2. **10–20 min:** Use an AI model of your choice to answer the prompts. Save its outputs locally with the same case IDs. Record the model name/version, generation settings and date in your own experiment notes.
3. **20–30 min:** Compare your report with a manual review. Find a false positive or false negative in a deterministic check.
4. **30–45 min:** Propose one focused improvement with evidence, then contribute a test, useful case or documentation change.

No model access? Edit a demo response to intentionally fail and use the failure report to understand each evaluator. Model execution is separate from this toolkit.

## Starter tasks with acceptance criteria

### 1. Add a Spanish learning case

Add one original Spanish open-source literacy prompt and matching demo response. Explain why the chosen check is useful and what it misses. Keep IDs unique, update documented counts, and pass the full test suite.

### 2. Add a numeric-tolerance check

Propose a `numeric` check with an expected finite number and nonnegative absolute tolerance. Document accepted response syntax. Include tests for boundary tolerance, negative values, invalid values, NaN and infinity. Preserve existing checks and CLI exit-code behavior.

### 3. Explain a false positive with a reproducible example

Write a short educational example showing how `contains_all` can pass a wrong or contradictory answer. Include exact input, actual output and a better manual review rubric. Do not silently change the existing demo's meaning.

### 4. Add CSV report export

Add `--format csv` with a standard-library CSV writer. Include case ID, category, status and reason. Test commas, quotes, Unicode and newlines; explain safe handling when opening untrusted cell content in spreadsheet applications.

These are suggested tasks, not claimed or assigned issues. Check current discussions before starting overlapping work.

## Participation and recognition

The repository uses the `hacktoberfest` topic so people can discover it. Contributions are reviewed on their actual benefit, not their count. The project remains open to contributions all year.

According to the [official Hacktoberfest 2026 FAQ](https://hacktoberfest.com/questions), PR/MR counts no longer count toward rewards; the event now emphasizes community building and learning around open-source AI. Creating this repository does not register anyone for an event or guarantee rewards. Follow the official event instructions separately.

中文：本项目欢迎有实际价值的代码、评测用例、翻译和文档贡献。2026 年官方活动规则已变化，请以官网为准；仓库创建与主题标签不等同于活动报名。
