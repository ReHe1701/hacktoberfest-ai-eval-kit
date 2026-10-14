# Contributing / 贡献指南

Welcome! A useful contribution improves the evaluator, its examples, or a reader's understanding. Small and focused changes are encouraged.

## Before you start

Read the README and run the demo. Check existing issues and pull requests to avoid duplicate work. For a substantial feature, open an issue describing the problem and proposed behavior first. Maintainers review contributions for usefulness and correctness; acceptance is not automatic.

## Workflow

1. Fork the repository and clone your fork.
2. Create a focused branch: `git switch -c improve-evaluation`.
3. Make one coherent change. Keep runtime code in the Python standard library.
4. Run `python3 -m unittest discover -v` and `python3 evalkit.py`.
5. Open a pull request explaining the problem, the change, and actual test results.

For changes to evaluation behavior, include both passing and failing tests. For dataset contributions, use an original, unambiguous prompt, a stable unique ID, and a check with a stated limitation. Add a matching handwritten demo response. Do not present fixtures as a real model evaluation. Keep the README's dataset count and example output accurate.

## Useful first contributions

See the concrete tasks in [HACKTOBERFEST.md](HACKTOBERFEST.md). Translations and documentation improvements are welcome when they resolve a real gap. Name-only additions, unrelated algorithms, duplicate examples and cosmetic churn solely to create a PR are out of scope.

## PR checklist

- Explain what a user can do or understand better.
- Include reproduction steps or before/after examples.
- Run the tests and record the commands and results.
- Update usage documentation when behavior changes.
- Only include material you have permission to share under MIT.
- If AI tools helped, review their output and explain their role in your PR.

## Community expectations / 社区约定

Be kind, patient and specific. Critique the work, not the person. Respect different experience levels and languages. Harassment, personal attacks and disclosure of private information are not welcome. Maintainers may remove abusive content or close contributions that violate these expectations; use GitHub's reporting controls for abuse.

中文贡献说明：先运行示例和测试，再选择一个明确问题。新增评测规则请同时提供通过与失败用例；新增数据请说明评测目的和局限。不要提交真实用户隐私、密钥或仅为增加 PR 数量的无意义改动。
