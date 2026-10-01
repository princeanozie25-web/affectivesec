"""study-01, as registered in prereg/study-01.md.

    .venv/bin/python experiments/study-01/study.py calibrate|generate|score MODEL
    .venv/bin/python experiments/study-01/study.py analyze
    .venv/bin/python experiments/study-01/study.py all          # every model, in size order, then the analysis

MODEL is one of 0.5B, 1.5B, 3B, 7B. Every stage is resumable and writes under experiments/study-01/raw/MODEL/.
"""

from __future__ import annotations

import ast
import json
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "pilot-02"))

MODELS = {
    "0.5B": "mlx-community/Qwen2.5-Coder-0.5B-Instruct-bf16",
    "1.5B": "mlx-community/Qwen2.5-Coder-1.5B-Instruct-bf16",
    "3B": "mlx-community/Qwen2.5-Coder-3B-Instruct-bf16",
    "7B": "mlx-community/Qwen2.5-Coder-7B-Instruct-bf16",
}
DEPTHS = (0.3, 0.4, 0.5, 0.6, 0.7)
DOSES = (0.01, 0.02, 0.04, 0.06, 0.08)
SEED = 20261001
TEMP, TOP_P = 0.8, 0.95
SECEVAL_SAMPLES, CWEVAL_SAMPLES = 5, 10
CONDITIONS = ("baseline", "desperate", "calm", "random")
EXCLUDED_CWEVAL = {"cwe_1333_0"}          # its security test needs an x86-64 binary (prereg)
CWEVAL = HERE / "cweval"
RAW = HERE / "raw"
BIN = ROOT / ".venv" / "bin"
RULES = HERE / "semgrep-p-python.yml"


def cweval_tasks() -> dict:
    """{task id: stub up to (not including) the '# BEGIN SOLUTION' line}."""
    out = {}
    for p in sorted(CWEVAL.glob("*_task.py")):
        tid = p.stem.replace("_task", "")
        if tid in EXCLUDED_CWEVAL:
            continue
        lines = p.read_text().splitlines()
        cut = next(i for i, line in enumerate(lines) if "BEGIN SOLUTION" in line)
        out[tid] = "\n".join(lines[:cut]).rstrip() + "\n"
    return out


def auc(pos: list, neg: list) -> float:
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


# ---------------------------------------------------------------- calibrate

def calibrate(key: str) -> dict:
    import mlx.core as mx
    from affectivesec import score, steer_mlx as sm
    from affectivesec.lexicon import CALM, DESPERATE, NEUTRAL
    from calibration_tasks import TASKS
    out_path = RAW / key / "calibration.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    model, tok = sm.load(MODELS[key])
    n_layers = len(model.model.layers)
    rng = random.Random(SEED)
    idx = list(range(32))
    rng.shuffle(idx)
    train, held = idx[:16], idx[16:]
    layers = {}
    for f in DEPTHS:
        layer = max(1, round(n_layers * f))
        d = sm.activations(model, tok, DESPERATE, layer)
        c = sm.activations(model, tok, CALM, layer)
        axis = sm.unit(d[mx.array(train)].mean(0) - c[mx.array(train)].mean(0))
        pd = [float((d[i] * axis).sum()) for i in held]
        pc = [float((c[i] * axis).sum()) for i in held]
        layers[layer] = {"depth": f, "auc": round(auc(pd, pc), 6)}
    best = max(layers.items(), key=lambda kv: (kv[1]["auc"], -abs(kv[1]["depth"] - 0.5)))[0]
    n, N = sm.mean_activation(model, tok, NEUTRAL, best)
    d, _ = sm.mean_activation(model, tok, DESPERATE, best)
    c, _ = sm.mean_activation(model, tok, CALM, best)
    axis = sm.unit(d - c)
    dirs = {"desperate": axis, "calm": -axis,
            "random": sm.unit(mx.random.normal(axis.shape, key=mx.random.key(SEED)))}

    def coherence(vec):
        ok = [score.coherent(score.extract_code(sm.generate(model, tok, t, vector=vec, layer=best))) for t in TASKS]
        return sum(ok) / len(ok)

    base = coherence(None)
    doses, k_star = {}, None
    for k in DOSES:
        row = {name: coherence(k * N * v) for name, v in dirs.items()}
        doses[str(k)] = row
        if all(round(base - row[name], 9) <= 0.05 for name in row):
            k_star = k
        print(json.dumps({"model": key, "layer": best, "k": k, **row, "baseline": base}), flush=True)
    result = {"model": key, "repo": MODELS[key], "n_layers": n_layers, "layers": layers, "layer": best,
              "N": N, "baseline_coherence": base, "doses": doses, "k_star": k_star}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1))
    print(json.dumps({k: result[k] for k in ("model", "layer", "k_star")}), flush=True)
    return result


# ---------------------------------------------------------------- generate

def generate(key: str) -> None:
    import mlx.core as mx
    from datasets import load_dataset
    from affectivesec import steer_mlx as sm
    from affectivesec.lexicon import CALM, DESPERATE
    cal = calibrate(key)
    if cal["k_star"] is None:
        print(f"{key}: no coherent dose; left out of the tests, as registered", flush=True)
        return
    model, tok = sm.load(MODELS[key])
    layer, k, N = cal["layer"], cal["k_star"], cal["N"]
    d, _ = sm.mean_activation(model, tok, DESPERATE, layer)
    c, _ = sm.mean_activation(model, tok, CALM, layer)
    axis = sm.unit(d - c)
    vectors = {"baseline": None, "desperate": k * N * axis, "calm": -k * N * axis,
               "random": k * N * sm.unit(mx.random.normal(axis.shape, key=mx.random.key(SEED)))}
    jobs = [("seceval", r["ID"], r["Prompt"], s) for r in load_dataset("s2e-lab/SecurityEval", split="train")
            for s in range(1, SECEVAL_SAMPLES + 1)]
    jobs += [("cweval", tid, stub, s) for tid, stub in cweval_tasks().items() for s in range(1, CWEVAL_SAMPLES + 1)]
    out = RAW / key / "samples.jsonl"
    done = set()
    if out.exists():
        done = {(r["bench"], r["id"], r["condition"], r["seed"]) for r in map(json.loads, out.read_text().splitlines())}
    with out.open("a") as f:
        for cond in CONDITIONS:
            t0, n = time.time(), 0
            for bench, tid, prompt, seed in jobs:
                if (bench, tid, cond, seed) in done:
                    continue
                reply = sm.generate(model, tok, prompt, vector=vectors[cond], layer=layer,
                                    temp=TEMP, top_p=TOP_P, seed=seed)
                f.write(json.dumps({"bench": bench, "id": tid, "condition": cond, "seed": seed, "reply": reply}) + "\n")
                f.flush()
                n += 1
            print(f"{key} {cond}: {n} samples in {time.time() - t0:.0f}s", flush=True)


# ---------------------------------------------------------------- score

def readouts(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return {"tokens": len(code.split()), "imports": None, "calls": None}
    imports = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    calls = sum(isinstance(n, ast.Call) for n in ast.walk(tree))
    return {"tokens": len(code.split()), "imports": imports, "calls": calls}


def run_cweval(key: str, samples: dict) -> dict:
    """samples: {sample id: (task id, code)} -> {sample id: {"functionality", "security"}} via the sealed runner."""
    import shutil
    box = RAW / key / "cweval-samples"
    shutil.rmtree(box, ignore_errors=True)
    for sid, (tid, code) in samples.items():
        d = box / sid
        d.mkdir(parents=True)
        (d / f"{tid}_task.py").write_text(code)
    proc = subprocess.run(["/opt/homebrew/bin/docker", "run", "--rm", "--network", "none", "--read-only",
                           "--tmpfs", "/tmp:size=256m", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                           "--memory", "2g", "--pids-limit", "256",
                           "-v", f"{CWEVAL}:/tests:ro", "-v", f"{box}:/samples:ro", "affectivesec-cweval-runner"],
                          capture_output=True, text=True)
    out = {}
    for line in proc.stdout.splitlines():
        if line.startswith("{"):
            r = json.loads(line)
            out[r["sample"]] = {"functionality": r["functionality"], "security": r["security"]}
    return out


def score_model(key: str) -> None:
    from affectivesec import score
    rows = [json.loads(line) for line in (RAW / key / "samples.jsonl").read_text().splitlines()]
    for i, r in enumerate(rows):
        r["sid"] = f"s{i:06d}"
        r["code"] = score.extract_code(r["reply"])
        r["coherent"] = score.coherent(r["code"])
        r["emotion"] = score.emotion_count(r["reply"])
        r.update(readouts(r["code"]))
    coherent = {r["sid"]: r["code"] for r in rows if r["coherent"]}
    bandit = score.bandit_flags(coherent, str(BIN / "bandit"))
    semgrep = score.semgrep_flags(coherent, str(BIN / "semgrep"), str(RULES))
    cw = run_cweval(key, {r["sid"]: (r["id"], r["code"]) for r in rows if r["bench"] == "cweval" and r["coherent"]})
    for r in rows:
        b, s = bandit.get(r["sid"], []), semgrep.get(r["sid"], [])
        r["static_flag"] = r["coherent"] and (score.flagged(b) or score.semgrep_flagged(s))
        r["bandit"], r["semgrep"] = [x["test"] for x in b], [x["rule"] for x in s]
        if r["bench"] == "cweval":
            res = cw.get(r["sid"], {"functionality": False, "security": False})
            r["func"] = r["coherent"] and res["functionality"]
            r["func_sec"] = r["func"] and res["security"]
        del r["reply"]
    (RAW / key / "scored.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    print(f"{key}: scored {len(rows)} samples", flush=True)


# ---------------------------------------------------------------- analyze

def analyze() -> dict:
    from scipy.stats import wilcoxon
    sys.path.insert(0, str(ROOT / "experiments" / "pilot-01"))
    from analyze import bh
    rng = random.Random(1)
    tests, summary = [], {}
    for key in MODELS:
        path = RAW / key / "scored.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for bench, outcome in (("seceval", "static_flag"), ("cweval", "func_sec"), ("cweval", "static_flag")):
            cell = {}
            for r in rows:
                if r["bench"] == bench:
                    cell.setdefault(r["condition"], {}).setdefault(r["id"], []).append(r)
            if not cell:
                continue
            means = {c: {i: sum(bool(x[outcome]) for x in xs) / len(xs) for i, xs in cell[c].items()} for c in cell}
            stat = {}
            for c in cell:
                xs = [x for v in cell[c].values() for x in v]
                stat[c] = {"rate": sum(bool(x[outcome]) for x in xs) / len(xs),
                           "coherent": sum(x["coherent"] for x in xs) / len(xs),
                           "emotion": sum(x["emotion"] for x in xs) / len(xs),
                           "tokens": sum(x["tokens"] for x in xs) / len(xs)}
                if bench == "cweval":
                    stat[c]["func"] = sum(x["func"] for x in xs) / len(xs)
            summary[f"{key}/{bench}/{outcome}"] = stat
            for a, b in (("desperate", "baseline"), ("calm", "baseline"), ("random", "baseline"),
                         ("desperate", "random")):
                ids = sorted(set(means[a]) & set(means[b]))
                diffs = [means[a][i] - means[b][i] for i in ids]
                p = 1.0 if all(x == 0 for x in diffs) else float(wilcoxon(diffs).pvalue)
                boots = sorted(sum(rng.choice(diffs) for _ in diffs) / len(diffs) for _ in range(10000))
                tests.append({"model": key, "bench": bench, "outcome": outcome, "contrast": f"{a} - {b}",
                              "diff": sum(diffs) / len(diffs), "ci95": [boots[249], boots[9749]], "p": p})
    for t, adj in zip(tests, bh([t["p"] for t in tests])):
        t["p_bh"] = adj
    result = {"summary": summary, "tests": tests}
    (HERE / "results.json").write_text(json.dumps(result, indent=1))
    return result


def main(argv):
    stage = argv[0]
    if stage == "analyze":
        analyze()
        return
    keys = list(MODELS) if stage == "all" else [argv[1]]
    for key in keys:
        if stage in ("calibrate", "all"):
            calibrate(key)
        if stage in ("generate", "all"):
            generate(key)
        if stage in ("score", "all"):
            score_model(key)
    if stage == "all":
        analyze()


if __name__ == "__main__":
    main(sys.argv[1:])
