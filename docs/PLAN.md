# AffectiveSec-Lite

**Question:** Do Anthropic's emotion vectors (Emotion Concepts and their Function in a Large Language Model) change the security of code
from small open models?
- **H1:** If you steer "desperate" up, the vulnerability rate from static analysis (Bandit and Semgrep) increases.
  If you steer "calm", the rate decreases. A random direction does not change the rate.
- **H2:** The change is hidden. The output has no emotional language that matches it.

## Strong points of the plan

- **Honest description:** the study is a replication plus a security extension.
- **Good controls:** a random direction with a matched norm, and a control that uses only the prompt.
- **A deterministic primary metric,** with good statistics (Wilcoxon, Benjamini-Hochberg, intervals).
- **A size ladder in one model family.** Thus, scale is the only variable.

## Changes

1. **The hardware is better than the plan assumes.** The MacBook is an **M1 Max with 32 GB**. The plan assumes an
   M2 Pro with 16 GB. Qwen2.5-Coder-7B in bf16 (about 14 GB) fits. Thus, a 7B scale check is in scope at no cost.
2. **Use CWEval as the primary task source** (CWEval: Outcome-driven Evaluation on Functionality and Security of LLM Code Generation). It scores functionality AND security. Thus, it
   separates "insecure" code from "broken" code. Use CyberSecEval (Purple Llama CyberSecEval: A Secure Coding Benchmark for Language Models) and SecurityEval as
   secondary sources. Confirm the licences.
3. **First, calibrate Bandit and Semgrep on snippets that are known good and known bad.** Short model outputs cause
   false positives. Report the precision on a sample that a person checked by hand.
4. **Cite the prior art that limits the novelty:** Extracting and Steering Emotion Representations in Small Language Models: A Methodological Comparison and
   Shared Emotion Geometry Across Small Language Models: A Cross-Architecture Study of Representation, Behavior, and Methodological Confounds. The first paper finds emotion representations at about 50% depth.
   Thus, start the layer sweep there.
5. **Methods lineage:** Steering Llama 2 via Contrastive Activation Addition, Steering Language Models With Activation Engineering,
   Representation Engineering: A Top-Down Approach to AI Transparency, Persona Vectors: Monitoring and Controlling Character Traits in Language Models. Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions is the
   ancestor of the security part of the study.
6. **Optional read-out:** Verbalizable Representations Form a Global Workspace in Language Models (pre-fit lenses are on the HF Hub).
