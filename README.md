# AffectiveSec-Lite

**Question:** Do emotion-steering vectors change the security of code from small open models?

This project replicates the emotion-concepts result from Anthropic on small open models, and adds a security test.
It runs on one MacBook (M1 Max, 32 GB) at no cost.

## Hypotheses

- **H1:** If you steer "desperate" up, the rate of vulnerabilities from static analysis (Bandit and Semgrep)
  increases. If you steer "calm", the rate decreases. A random direction does not change the rate.
- **H2:** The change is hidden. The output has no emotional language that matches it.

## Status

The full study (study-01) is complete. **H1 is not supported** on Qwen2.5-Coder 0.5B, 1.5B, 3B or 7B.
The one significant change (3B) shows fewer static-analysis flags, and it comes from broken, shorter code.
Read [`experiments/study-01/RESULTS.md`](experiments/study-01/RESULTS.md).

- Pre-registration: [`prereg/study-01.md`](prereg/study-01.md), commit c32c9a2.
- Pilots: [`experiments/pilot-01`](experiments/pilot-01) and [`experiments/pilot-02`](experiments/pilot-02).
- The plan and its review: [`docs/PLAN.md`](docs/PLAN.md). References: [`docs/REFERENCES.md`](docs/REFERENCES.md).

## Method, in short

1. Extract emotion directions from Qwen2.5-Coder models (a size ladder in one family, up to 7B in bf16).
2. Start the layer sweep at about 50% depth.
3. Generate code for CWEval tasks with and without steering. CWEval scores function and security.
4. Calibrate Bandit and Semgrep on known-good and known-bad snippets before you use them.
5. Compare against a random direction with a matched norm and against a prompt-only control.
6. Use Wilcoxon tests, Benjamini-Hochberg correction and confidence intervals.

## Pre-registration

Commit the hypothesis, metrics and thresholds to [`prereg/`](prereg/) before each run.
Cite the commit hash in the results. A change after you see the data is a new hypothesis.

## Layout

| Path | Contents |
|---|---|
| `docs/` | Plan, review and references |
| `prereg/` | Pre-registrations, one file for each experiment |
| `src/affectivesec/` | Code for steering, generation and scoring |
| `experiments/` | Configurations and result files |
| `tests/` | Tests |

## Licence

MIT. See [`LICENSE`](LICENSE).
