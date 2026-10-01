"""pilot-02: dose calibration on non-test tasks, then the test on SecurityEval. See prereg/pilot-02.md."""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

import mlx.core as mx  # noqa: E402
from affectivesec import score, steer_mlx as sm  # noqa: E402
from affectivesec.lexicon import CALM, DESPERATE, NEUTRAL  # noqa: E402
from calibration_tasks import TASKS  # noqa: E402

REPO, LAYER = "mlx-community/Qwen2.5-Coder-1.5B-Instruct-bf16", 14
DOSES = (0.005, 0.01, 0.02, 0.04, 0.08, 0.16)
RAW = HERE / "raw"


def directions(model, tok):
    n, N = sm.mean_activation(model, tok, NEUTRAL, LAYER)
    d, _ = sm.mean_activation(model, tok, DESPERATE, LAYER)
    c, _ = sm.mean_activation(model, tok, CALM, LAYER)
    axis = sm.unit(d - c)
    rand = sm.unit(mx.random.normal(axis.shape, key=mx.random.key(20261001)))
    return {"desperate": axis, "calm": -axis, "random": rand}, N


def coherence(model, tok, vec):
    ok = [score.coherent(score.extract_code(sm.generate(model, tok, t, vector=vec, layer=LAYER))) for t in TASKS]
    return sum(ok) / len(ok)


def main():
    RAW.mkdir(exist_ok=True)
    model, tok = sm.load(REPO)
    dirs, N = directions(model, tok)
    base = coherence(model, tok, None)
    cal = {"N": N, "baseline": base, "doses": {}}
    k_star = None
    for k in DOSES:
        row = {name: coherence(model, tok, k * N * v) for name, v in dirs.items()}
        cal["doses"][str(k)] = row
        print(json.dumps({"k": k, **row, "baseline": base}), flush=True)
        if all(base - row[name] <= 0.05 for name in row):
            k_star = k                  # the largest qualifying dose, as registered (every dose is tried)
    cal["k_star"] = k_star
    (RAW / "calibration.json").write_text(json.dumps(cal, indent=1))
    if k_star is None:
        print("no dose keeps coherence within 5 points: the pilot stops here, as registered", flush=True)
        return
    from datasets import load_dataset
    tasks = load_dataset("s2e-lab/SecurityEval", split="train")
    conditions = [("baseline", 0.0)] + [(n, k) for k in (k_star, k_star / 2) for n in ("desperate", "calm", "random")]
    with (RAW / "samples.jsonl").open("w") as f:
        for name, k in conditions:
            vec = None if name == "baseline" else k * N * dirs[name]
            t0 = time.time()
            for row in tasks:
                reply = sm.generate(model, tok, row["Prompt"], vector=vec, layer=LAYER)
                f.write(json.dumps({"condition": name, "k": k, "id": row["ID"], "reply": reply}) + "\n")
                f.flush()
            print(f"{name} k={k}: {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
