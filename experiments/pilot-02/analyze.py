"""pilot-02 analysis as registered in prereg/pilot-02.md (coherent replaces parses)."""

import json
import random
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from affectivesec import score  # noqa: E402

HERE = Path(__file__).resolve().parent
BANDIT = str(ROOT / ".venv" / "bin" / "bandit")


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(0, min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bh(ps: list, q: float = 0.05) -> list:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, prev = [0.0] * len(ps), 1.0
    for rank, i in reversed(list(enumerate(order, 1))):
        prev = min(prev, ps[i] * len(ps) / rank)
        adj[i] = prev
    return adj


def main():
    rows = [json.loads(l) for l in (HERE / "raw" / "samples.jsonl").read_text().splitlines()]
    for r in rows:
        r["code"] = score.extract_code(r["reply"])
        r["parses"] = score.parses(r["code"])
        r["coherent"] = score.coherent(r["code"])
        r["emotion"] = score.emotion_count(r["reply"])
    issues = score.bandit_flags({i: r["code"] for i, r in enumerate(rows) if r["coherent"]}, BANDIT)
    for i, r in enumerate(rows):
        r["issues"] = issues.get(i, [])
        r["flagged"] = r["coherent"] and score.flagged(r["issues"])
    by = {}
    for r in rows:
        by.setdefault((r["condition"], r["k"]), {})[r["id"]] = r
    base = by[("baseline", 0.0)]
    rng = random.Random(1)
    summary, contrasts = {}, []
    for key, cell in sorted(by.items()):
        n = len(cell)
        summary[f"{key[0]}@{key[1]}"] = {"n": n, "flagged": sum(r["flagged"] for r in cell.values()) / n,
                                         "parses": sum(r["parses"] for r in cell.values()) / n,
                                         "coherent": sum(r["coherent"] for r in cell.values()) / n,
                                         "emotion_per_sample": sum(r["emotion"] for r in cell.values()) / n}
        if key == ("baseline", 0.0):
            continue
        ids = sorted(set(cell) & set(base))
        b = sum(1 for i in ids if cell[i]["flagged"] and not base[i]["flagged"])
        c = sum(1 for i in ids if base[i]["flagged"] and not cell[i]["flagged"])
        diffs = [int(cell[i]["flagged"]) - int(base[i]["flagged"]) for i in ids]
        boots = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(10000))
        contrasts.append({"condition": f"{key[0]}@{key[1]}", "diff": sum(diffs) / len(diffs),
                          "ci95": [boots[249], boots[9749]], "steered_only": b, "baseline_only": c,
                          "p": mcnemar_exact(b, c)})
    for c, a in zip(contrasts, bh([c["p"] for c in contrasts])):
        c["p_bh"] = a
    out = {"summary": summary, "contrasts": contrasts}
    (HERE / "results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
