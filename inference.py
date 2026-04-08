"""OpenAI baseline runner with strict structured submission logs.

Required env vars (api mode): API_BASE_URL, MODEL_NAME, and HF_TOKEN (or OPENAI_API_KEY).
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

from openai import OpenAI
import signal

from env import Action, SupportEnv, TASKS, TICKETS, grade

def _timeout_handler(signum, frame):
    raise TimeoutError("Inference exceeded MAX_RUNTIME_SECONDS \u2014 aborting.")

def _install_timeout(seconds: int) -> None:
    """Install a SIGALRM-based hard timeout (Unix only)."""
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(seconds)

def _cancel_timeout() -> None:
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)

BENCHMARK = os.getenv("BENCHMARK", "support-ticket-env")

# Required by submission checklist.
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME", "").strip()


def _emit_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def _emit_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    done_str = str(done).lower()
    err_str = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={err_str}", flush=True)


def _emit_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    success_str = str(success).lower()
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


def parse_model_output(raw: str) -> Action:
    """Parse model text output into a typed Action with safe defaults."""
    fields: dict[str, str] = {}
    for line in raw.strip().splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip().lower()] = value.strip()

    return Action(
        category=fields.get("category", "unknown"),
        priority=fields.get("priority", "medium"),
        action=fields.get("action", "guide"),
        response=fields.get("response", ""),
        resolve=fields.get("resolve", "false").lower() == "true",
    )


def build_prompt(task_id: str, user_query: str, history: list[str]) -> str:
    """Build a deterministic task-specific prompt for the model."""
    task = TASKS[task_id]
    return (
        "You are a customer support triage agent.\n"
        f"Task difficulty: {task.difficulty}\n"
        f"Task objective: {task.objective}\n"
        "Return ONLY the following keys, one per line:\n"
        "category: <billing|account|technical>\n"
        "priority: <low|medium|high>\n"
        "action: <refund|escalate|guide>\n"
        "response: <short customer-facing response>\n"
        "resolve: <true|false>\n\n"
        f"User query: {user_query}\n"
        f"Conversation history: {history}\n"
    )


def call_model(client: OpenAI, prompt: str, model: str) -> str:
    """Call OpenAI Chat Completions with deterministic settings."""
    seed = int(os.getenv("OPENAI_SEED", "7"))
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        top_p=1,
        seed=seed,
        messages=[
            {"role": "system", "content": "Follow the requested output format exactly."},
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content or ""


def mock_model_output(expected: dict, step: int) -> str:
    """Deterministic oracle output for validated task indices (1, 2, 12)."""
    # Hard mode (index 12) needs 2 steps: one triage, one resolve.
    is_hard = expected.get("id") == "TKT-013"
    resolve_value = "false"
    if not is_hard or (is_hard and step >= 2):
        resolve_value = "true"

    if expected["action"] == "refund":
        resp = "We processed a refund for the duplicate charge."
    elif expected["action"] == "escalate":
        resp = "Escalating this critical issue to our engineering team."
    else:
        resp = "Please follow the guide in our help center."

    return (
        f"category: {expected['category']}\n"
        f"priority: {expected['priority']}\n"
        f"action: {expected['action']}\n"
        f"response: {resp}\n"
        f"resolve: {resolve_value}"
    )


def run_task(task_id: str, client: Optional[OpenAI], model: str, mode: str) -> dict:
    """Run one task episode and emit strict START/STEP/END logs."""
    task = TASKS[task_id]
    expected = TICKETS[task.ticket_index]

    env = SupportEnv()
    obs = env.reset(task_id=task_id)
    done = False
    rewards: list[float] = []
    episode_return = 0.0
    info: dict = {"step": 0}
    last_error: Optional[str] = None
    action = Action(category="unknown", priority="medium", action="guide", response="", resolve=False)

    _emit_start(task=task_id, env=BENCHMARK, model=model)

    try:
        while not done:
            prompt = build_prompt(task_id=task_id, user_query=obs.user_query, history=obs.conversation_history)
            if mode == "mock":
                raw_output = mock_model_output(expected=expected, step=info["step"] + 1)
            else:
                if client is None:
                    raise RuntimeError("OpenAI client is required in api mode.")
                raw_output = call_model(client=client, prompt=prompt, model=model)

            action = parse_model_output(raw_output)
            obs, env_reward, done, info = env.step(action)

            reward_value = float(env_reward.score)
            rewards.append(reward_value)
            episode_return += reward_value

            action_str = (
                f"{action.action}(category={action.category},priority={action.priority},"
                f"resolve={str(action.resolve).lower()})"
            )
            _emit_step(
                step=int(info["step"]),
                action=action_str,
                reward=reward_value,
                done=bool(done),
                error=None,
            )
    except Exception as exc:
        last_error = str(exc)
    finally:
        close_fn = getattr(env, "close", None)
        if callable(close_fn):
            close_fn()

    grader_score = grade(task_id, action, expected)
    normalized_score = max(0.0, min(1.0, float(grader_score)))
    success = done and last_error is None
    _emit_end(success=success, steps=int(info.get("step", 0)), score=normalized_score, rewards=rewards)

    return {
        "task": task_id,
        "ticket_id": obs.ticket_id,
        "done": done,
        "step": int(info.get("step", 0)),
        "grader_score": normalized_score,
        "episode_return": round(episode_return, 4),
        "rewards": [round(r, 4) for r in rewards],
        "error": last_error,
    }


def run_baseline() -> None:
    """Run all tasks and write baseline artifact without extra stdout lines."""
    mode = os.getenv("BASELINE_MODE", "api").lower().strip()
    api_base_url = API_BASE_URL
    model = MODEL_NAME
    api_key = OPENAI_API_KEY or HF_TOKEN

    if mode != "mock":
        missing = [
            name
            for name, value in (
                ("API_BASE_URL", api_base_url),
                ("MODEL_NAME", model),
                ("HF_TOKEN or OPENAI_API_KEY", api_key),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required env vars in api mode: {', '.join(missing)}")

    seed = int(os.getenv("OPENAI_SEED", "7"))
    output_path = os.getenv("BASELINE_OUTPUT", "baseline_scores.json")
    max_runtime_seconds = int(os.getenv("MAX_RUNTIME_SECONDS", "1100"))
    _install_timeout(max_runtime_seconds)

    client = OpenAI(api_key=api_key, base_url=api_base_url) if mode != "mock" else None

    task_order = ["easy", "medium", "hard"]
    try:
        results = [run_task(task_id=t, client=client, model=model, mode=mode) for t in task_order]
    finally:
        _cancel_timeout()

    avg = sum(r["grader_score"] for r in results) / len(results)

    payload = {
        "model": model,
        "benchmark": BENCHMARK,
        "mode": mode,
        "seed": seed,
        "scores": [
            {
                "task": r["task"],
                "ticket_id": r["ticket_id"],
                "grader_score": r["grader_score"],
                "episode_return": r["episode_return"],
                "steps": r["step"],
                "rewards": r["rewards"],
                "error": r["error"],
            }
            for r in results
        ],
        "average_grader_score": round(avg, 4),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    elapsed = round(time.monotonic() - time.monotonic(), 3) # Placeholder for removal


if __name__ == "__main__":
    run_baseline()
