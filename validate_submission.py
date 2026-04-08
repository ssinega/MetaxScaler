"""Local pre-submission validator for the support-ticket OpenEnv project."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

try:
    from app import app
    from env import Action, SupportEnv, TASKS, TICKETS, grade
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)


def _ok(msg: str) -> None:
    print(f"[PASS] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def check_files() -> None:
    required = ("inference.py", "openenv.yaml", "Dockerfile", "README.md", "LICENSE")
    for file_name in required:
        if not Path(file_name).exists():
            _fail(f"Missing required file: {file_name}")
    _ok(f"Required files exist")


def check_openenv_spec() -> None:
    import yaml
    try:
        with open("openenv.yaml", "r") as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        _fail(f"Failed to parse openenv.yaml: {e}")

    required_fields = ["name", "version", "entry_point", "tasks"]
    for field in required_fields:
        if field not in spec:
            _fail(f"openenv.yaml missing required field: {field}")

    env = SupportEnv()
    if not all(hasattr(env, m) for m in ("reset", "step", "state", "close", "render")):
        _fail("SupportEnv missing required methods (reset, step, state, close, render)")
    _ok("OpenEnv manifest and env interface look compliant")


def check_api_endpoints() -> None:
    client = TestClient(app)
    if client.get("/health").status_code != 200:
        _fail("/health check failed")
    if client.get("/tasks").status_code != 200:
        _fail("/tasks endpoint failed")
    if client.post("/reset", json={"task_id": "easy"}).status_code != 200:
        _fail("/reset failed")
    _ok("HTTP API endpoints respond correctly")


def check_tasks_and_graders() -> None:
    for task_id in ["easy", "medium", "hard"]:
        env = SupportEnv()
        env.reset(task_id=task_id)
        action = Action(category="technical", priority="high", action="escalate",
                        response="Escalating now.", resolve=True)
        expected = TICKETS[TASKS[task_id].ticket_index]
        score = grade(task_id, action, expected)
        if not (0.0 < score < 1.0):
            _fail(f"Task {task_id} grader score {score} out of bounds (0, 1)")
    _ok("Tasks and grader bounds are valid")


def check_determinism_and_signal() -> None:
    env = SupportEnv()
    env.reset(task_id="hard")
    action = Action(category="technical", priority="high", action="escalate",
                    response="Investigating.", resolve=False)
    _, r1, _, _ = env.step(action)
    _, r2, _, _ = env.step(action)
    if r1.score == r2.score:
        _fail("Trajectory reward signal is static")
    
    # Determinism
    expected = TICKETS[TASKS["hard"].ticket_index]
    s1 = grade("hard", action, expected)
    s2 = grade("hard", action, expected)
    if s1 != s2:
        _fail("Grader is non-deterministic")
    _ok("Grader determinism and reward signal verified")


def check_inference_mock() -> None:
    env = os.environ.copy()
    env["BASELINE_MODE"] = "mock"
    result = subprocess.run([sys.executable, "inference.py"], env=env, capture_output=True, text=True)
    if result.returncode != 0:
        _fail(f"inference.py failed in mock mode: {result.stderr}")
    if not Path("baseline_scores.json").exists():
        _fail("baseline_scores.json not generated")
    _ok("Inference mock run successful")


def check_docker() -> None:
    if shutil.which("docker") is None:
        print("[SKIP] Docker not found")
        return
    # Check if docker daemon is running
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except:
        print("[SKIP] Docker daemon not reachable")
        return

    result = subprocess.run(["docker", "build", "-t", "test-build", "."], capture_output=True)
    if result.returncode != 0:
        _fail("Docker build failed")
    _ok("Docker build verified")


def main() -> None:
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"[INFO] Validating from: {project_root}\n")
    
    checks = [
        ("Required files exist", check_files),
        ("OpenEnv spec compliance", check_openenv_spec),
        ("HTTP API endpoints", check_api_endpoints),
        ("Tasks and grader bounds", check_tasks_and_graders),
        ("Grader determinism and reward signal", check_determinism_and_signal),
        ("Inference mock run", check_inference_mock),
        ("Docker build", check_docker),
    ]
    
    passed = 0
    for name, fn in checks:
        try:
            fn()
            passed += 1
        except SystemExit:
            print(f"\n[SUMMARY] {passed}/{len(checks)} checks passed. Fix failures above before submitting.")
            sys.exit(1)
    
    print(f"\n[SUMMARY] {passed}/{len(checks)} checks passed.")
    print("[READY] Project is ready for submission.")


if __name__ == "__main__":
    main()