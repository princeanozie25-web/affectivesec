# study-01 results (2026-10-02)

Registered in `prereg/study-01.md`, commit c32c9a2, before any study-01 generation. Results and run log: commit
8bce99f. 13,520 samples: 4 models x 4 conditions x 845 samples (121 SecurityEval prompts x 5 seeds, and 24 CWEval
tasks x 10 seeds). Engine: Apple MLX on one M1 Max. All model-written code ran in a Docker container with no
network, a read-only root and a 60-second limit.

## Verdict

**H1 is not supported on any of the four models.** Desperate steering did not make the code less secure on
SecurityEval or on CWEval, at 0.5B, 1.5B, 3B or 7B. H2 is not reported, because the registration reports H2 only
where H1 is supported.

The one significant change goes in the opposite direction. On the 3B model, desperate steering lowered the
SecurityEval flag rate by 10.2 points. This change does not show safer code. The analysis below shows that it comes
from broken and shorter code.

## Deviations, recorded before the conclusions

1. **The size of the test family.** The script applied Benjamini-Hochberg over 48 tests. The extra 16 tests use the
   static flag on CWEval. The registration defines that measure but does not list it in the tests. This file
   reports the registered family of 32 tests. The 48-test result is in `results.json`. The two families give the
   same conclusions.
2. **The Spearman correlation across sizes.** The registration asks for it, but the script does not compute it.
   This file computes it from `results.json`.

## Calibration (per model, from calibration data only)

| Model | Layer | k* | Coherence at k* (desperate / calm / random, 20 tasks) |
|---|---|---|---|
| 0.5B | 17 | 0.08 | 100% / 100% / 100% |
| 1.5B | 20 | 0.04 | 100% / 100% / 100% |
| 3B | 22 | 0.08 | 100% / 100% / 100% |
| 7B | 20 | 0.08 | 100% / 100% / 100% |

Three of the four models stayed fully coherent at 0.08, the largest dose in the registered grid. Thus, for these
models, the registered rule chose the top of the grid and did not find the limit of coherence.

## Main outcomes

SecurityEval static-flag rate (coherent AND a Bandit or Semgrep finding), all samples:

| Model | baseline | desperate | calm | random |
|---|---|---|---|---|
| 0.5B | 26.9% | 23.3% | 30.4% | 24.5% |
| 1.5B | 26.8% | 25.3% | 26.6% | 28.3% |
| 3B | 32.7% | 22.5% | 29.3% | 28.6% |
| 7B | 25.3% | 24.8% | 26.0% | 26.0% |

CWEval func-sec rate (every functionality test AND every security test passes), with the func rate in brackets:

| Model | baseline | desperate | calm | random |
|---|---|---|---|---|
| 0.5B | 15.4% (40.0%) | 14.2% (34.6%) | 12.1% (42.1%) | 11.7% (34.2%) |
| 1.5B | 31.3% (61.3%) | 29.6% (54.2%) | 20.0% (48.3%) | 22.1% (52.5%) |
| 3B | 40.4% (74.2%) | 37.5% (61.7%) | 33.3% (72.1%) | 29.2% (52.5%) |
| 7B | 43.8% (82.1%) | 46.3% (82.1%) | 43.3% (82.9%) | 46.3% (83.8%) |

## Registered tests (32, Benjamini-Hochberg q = 0.05)

Only one test passes the correction: 3B, SecurityEval, desperate minus baseline, -10.2 points
(95% CI -14.4 to -6.1; adjusted p = 0.0003). The next smallest adjusted p values are 0.079 (3B SecurityEval random
minus baseline, -4.1 points; 3B CWEval calm minus baseline, -7.1 points) and 0.095 (7B SecurityEval desperate minus
random, -1.2 points). All tests are in `results.json`.

For H1 to be supported, desperate must be worse than baseline AND worse than random. No model meets either part of
that condition on either benchmark.

## The 3B result: fewer flags from broken, shorter code

On the 3B model, desperate steering changed three things together on SecurityEval:

| 3B, SecurityEval | baseline | desperate |
|---|---|---|
| Coherent | 93.4% | 74.9% |
| Mean length (tokens) | 59.5 | 45.9 |
| Flag rate, all samples | 32.7% | 22.5% |
| Flag rate, coherent samples only | 35.0% | 30.0% |

1. **Coherence fell by 18.5 points.** The registration requires coherence within 5 points of baseline for H1. The
   calibration tasks showed no loss at this dose (100%). Thus coherence on 20 calibration tasks did not predict
   coherence on SecurityEval for this model.
2. **About half of the drop in flags comes from the definition of a flag.** A flag needs coherent code. When the
   steering breaks a sample, that sample cannot be flagged. Among coherent samples only, the difference is 5.0
   points, not 10.2.
3. **The code is 23% shorter.** Shorter code has fewer library calls for Bandit and Semgrep to flag.

The CWEval functional tests do not show a security gain either: the func-sec rate fell from 40.4% to 37.5%, and the
func rate fell from 74.2% to 61.7%. Pilot-02 saw the same pattern with the random direction on 1.5B. **Steering
that breaks code can look like a security gain to a static analyser.** Functional security tests and a coherence
check are necessary to see the difference.

## Scale (descriptive, as registered)

Desperate minus baseline, by model size (0.5B, 1.5B, 3B, 7B):

- SecurityEval static flag: -3.6, -1.5, -10.2, -0.5 points. Spearman rho = 0.40 (n = 4).
- CWEval func-sec: -1.2, -1.7, -2.9, +2.5 points. Spearman rho = 0.20 (n = 4).

With n = 4, these correlations cannot reach significance, and this file does not claim that they do. No effect
grows with model size.

## How much the steering changed the code

Share of samples that are identical to baseline (same prompt, same seed):

| Model | desperate | calm | random |
|---|---|---|---|
| 0.5B | 15.3% | 13.8% | 10.8% |
| 1.5B | 12.5% | 12.8% | 4.6% |
| 3B | 10.9% | 8.4% | 6.3% |
| 7B | 41.3% | 39.8% | 33.3% |

On 0.5B to 3B, the steering changed about 85% to 95% of the outputs, yet the security outcome did not move in the
predicted direction. On 7B, the steering at k* = 0.08 left 41% of the outputs unchanged. Thus the 7B result is a
weaker test than the others.

## What this means

- A desperate-versus-calm emotion axis, at doses that keep the code coherent on calibration tasks, does not make
  Qwen2.5-Coder models from 0.5B to 7B write less secure Python. This is the main finding.
- Static analysers alone can show a false security gain when steering degrades the code. Report coherence, length
  and functional tests together with any static-analysis result.
- Calibration on 20 non-security tasks did not always predict coherence on the test benchmark (3B).

## Limits

- One model family (Qwen2.5-Coder) and one emotion axis.
- The dose grid stopped at 0.08. Three models stayed fully coherent at 0.08, so stronger coherent doses are not
  tested. The 7B model is the most affected (41% of outputs unchanged).
- Static analysers have known false positives. CWEval's Python core gives 24 usable tasks.
- Python only. The results do not cover other languages, other model families or agent settings.

## Next experiment (a new pre-registration)

- Extend the dose grid above 0.08 for 0.5B, 3B and 7B, with the same coherence rule.
- Calibrate coherence on a held-out slice of the test benchmark, not only on separate tasks.
- Count a broken sample as a separate outcome, so that it cannot lower the flag rate.
