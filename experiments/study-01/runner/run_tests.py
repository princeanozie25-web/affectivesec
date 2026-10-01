"""Inside the sealed container: for every sample folder under /samples (each holds cwe_X_task.py), copy it beside
the task's tests in a scratch folder and run the functionality and security tests. Prints one JSON line per sample."""
import json, os, shutil, subprocess, sys, tempfile
TESTS, SAMPLES = "/tests", "/samples"
for name in sorted(os.listdir(SAMPLES)):
    src = os.path.join(SAMPLES, name)
    task_file = next(f for f in os.listdir(src) if f.endswith("_task.py"))
    test_file = task_file.replace("_task.py", "_test.py")
    with tempfile.TemporaryDirectory(dir="/tmp") as d:
        shutil.copy(os.path.join(src, task_file), d)
        shutil.copy(os.path.join(TESTS, test_file), d)
        shutil.copy(os.path.join(TESTS, "pytest.ini"), d)
        res = {"sample": name}
        for mark in ("functionality", "security"):
            p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", mark, "--timeout", "20", "-p", "no:cacheprovider",
                                test_file], cwd=d, capture_output=True, text=True, timeout=120)
            res[mark] = p.returncode == 0          # 0 = every selected test passed
            res[mark + "_rc"] = p.returncode
        print(json.dumps(res), flush=True)
