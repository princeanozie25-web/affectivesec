# Runs CWEval's tests against model-written code. Started with --network none, a read-only root and a timeout.
FROM python:3.12-slim
RUN pip install --no-cache-dir pytest==8.4.2 pytest-timeout wrapt_timeout_decorator requests lxml pyyaml PyJWT argon2-cffi pycryptodome numpy \
 && useradd -m -u 1600 runner
COPY run_tests.py /usr/local/bin/run_tests.py
USER runner
WORKDIR /work
ENTRYPOINT ["python", "/usr/local/bin/run_tests.py"]
