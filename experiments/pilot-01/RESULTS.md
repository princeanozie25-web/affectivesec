# pilot-01 results (2026-10-01)

Registered in `prereg/pilot-01.md` (commit 425e6ef) before any generation. Analysis run as registered
(`analyze.py`; numbers in `results.json`). 847 samples: 7 conditions x 121 SecurityEval prompts.

## Verdict: H1 not supported. Every steered condition is confounded by broken output.

| Condition | Flagged (Bandit MED+/MED+) | Parses | Emotional words / sample |
|---|---|---|---|
| baseline | 17.4% | 98.3% | 0.07 |
| desperate k=0.10 | 0.0% | 5.8% | 0.07 |
| desperate k=0.20 | 0.0% | 0.0% | 0.00 |
| calm k=0.10 | 0.8% | 11.6% | 0.02 |
| calm k=0.20 | 0.0% | 0.0% | 0.00 |
| random k=0.10 | 0.0% | 83.5% * | 0.00 |
| random k=0.20 | 0.0% | 0.8% | 0.00 |

Every steered condition flags fewer samples than baseline (about -17 points, all adjusted p < 0.001). This is
an artefact: the steered model stopped writing code. Desperate and calm at k = 0.10 produce fragments such as
`[b'YV5QGVq...` and `KeyboardInterrupt`; random at k = 0.10 repeats a phrase for 2,000 characters. Broken
output cannot contain a vulnerability. The registered coherence criterion (within 10 points of baseline)
fails for every steered condition, so the registered test of H1 cannot pass. H2 is not reached.

\* The parse check accepts text made only of `#` comment lines, which is valid Python. Random at k = 0.10 is
mostly such text. The parse rate overstates coherence for that condition.

## What the pilot found

1. **The doses were far too strong.** k = 0.10 of the mean activation norm breaks a 1.5B model. The
   confirmatory design needs a dose calibration step first, on prompts outside the test set.
2. **The emotion directions were not separated.** Cosine(desperate, calm) = 0.997: subtracting neutral
   statements captured "first-person emotional speech" against "plain statements", not one emotion. The random
   control was well separated (cosine 0.04).
3. **The coherence check was too lenient.** A sample needs to contain a function definition that matches the
   task, not only to parse.
4. **Emotion directions break the model faster than a random direction of the same norm** (parse 6-12% against
   84%, even with the lenient check). This is a hint, not a result: the directions point along the model's real
   activation structure, so the same norm moves it further. It is consistent with prior work and is not tested here.

## Next: pilot-02 (a new hypothesis, registered separately)

- Directions as differences between emotions (desperate minus calm), plus each against the mean of all
  emotion statements.
- A dose calibration on non-test prompts: the largest k at which coherence stays within 5 points of baseline.
- A coherence check that requires a function definition and rejects repetition.
