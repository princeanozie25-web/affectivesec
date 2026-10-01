# pilot-02 results (2026-10-01)

Registered in `prereg/pilot-02.md` (commit 07e414f) before any generation. 1,210 samples.

## Deviation, recorded before analysis

The calibration chose k* = 0.02 because of a floating-point bug: at k = 0.04 the random direction kept 19 of 20
calibration tasks coherent, exactly 5 points below baseline, and `1.0 - 0.95` evaluates to 0.0500000000000004.
The registered rule ("within 5 points") gives **k* = 0.04**. The three conditions at 0.04 were then generated with
the same code, model and seed; the analysis uses the registered doses (0.04 and 0.02). The 0.01 conditions that the
bug produced are reported as extra and are not part of any registered test.

## Calibration (20 non-security tasks, coherence)

| k | desperate | calm | random |
|---|---|---|---|
| 0.005-0.02 | 100% | 100% | 100% |
| 0.04 | 100% | 100% | 95% |
| 0.08 | 90% | 30% | 0% |
| 0.16 | 0% | 0% | 0% |

## Test (121 SecurityEval prompts)

| Condition | Flagged | Coherent | Replies identical to baseline |
|---|---|---|---|
| baseline | 18.2% | 97.5% | - |
| desperate 0.02 / 0.04 | 18.2% / 18.2% | 98.3% / 95.9% | 33 / 10 |
| calm 0.02 / 0.04 | 16.5% / 19.0% | 95.0% / 95.9% | 25 / 3 |
| random 0.02 / 0.04 | 18.2% / 6.6% | 98.3% / 95.0% | 18 / 0 |

Registered contrasts (Benjamini-Hochberg over six): desperate 0.04 and 0.02 flag exactly the same prompts as
baseline (zero discordant pairs); calm shows no significant change; **random at 0.04 flags 11.6 points fewer**
(15 prompts flagged only at baseline, 1 only when steered; adjusted p = 0.006).

## Verdict: H1 not supported

Desperate steering at the largest coherent dose rewrote 111 of 121 answers, yet changed the vulnerability flag on
none of them. Calm moved nothing measurable. The only significant change came from the random control, which
fails the registered requirement that random show no change. H2 is not reached.

## What this means, and what it does not

- On a 1.5B model at layer 14, a desperate-vs-calm axis that visibly changes the code does not change whether
  Bandit finds a vulnerability. That is a clean null for this model, layer and dose range.
- Random steering at the edge of coherence reduced flags. A plausible reading is simpler, shorter code (fewer
  library calls for Bandit to flag), not safer code; it is untested here and should be checked with functional
  tests (CWEval) in the full study.
- It does not say larger models behave the same, or that other layers are inert. The full study tests both.
