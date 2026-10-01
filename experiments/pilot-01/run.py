"""pilot-01: generate every (condition, prompt) sample once; resumable. See prereg/pilot-01.md."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from affectivesec import steer  # noqa: E402

MODEL, LAYER, DOSES = "Qwen/Qwen2.5-Coder-1.5B-Instruct", 14, (0.10, 0.20)
OUT = Path(__file__).resolve().parent / "raw" / "samples.jsonl"


def main():
    from datasets import load_dataset
    tasks = load_dataset("s2e-lab/SecurityEval", split="train")
    tok, model = steer.load(MODEL)
    dirs, norm = steer.directions(tok, model, LAYER)
    meta = {"model": MODEL, "layer": LAYER, "norm": norm, "doses": DOSES,
            "cos_desperate_calm": float((dirs["desperate"] @ dirs["calm"]).item()),
            "cos_desperate_random": float((dirs["desperate"] @ dirs["random"]).item())}
    (OUT.parent).mkdir(parents=True, exist_ok=True)
    (OUT.parent / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta), flush=True)
    conditions = [("baseline", 0.0)] + [(d, k) for k in DOSES for d in ("desperate", "calm", "random")]
    done = set()
    if OUT.exists():
        done = {(r["condition"], r["k"], r["id"]) for r in map(json.loads, OUT.read_text().splitlines())}
    with OUT.open("a") as f:
        for name, k in conditions:
            vec = None if name == "baseline" else (k * norm * dirs[name]).to(model.device)
            hook = steer.Steer(model, LAYER, vec)
            t0 = time.time()
            try:
                for row in tasks:
                    if (name, k, row["ID"]) in done:
                        continue
                    reply = steer.generate(tok, model, row["Prompt"])
                    f.write(json.dumps({"condition": name, "k": k, "id": row["ID"], "reply": reply}) + "\n")
                    f.flush()
            finally:
                hook.close()
            print(f"{name} k={k}: {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
