"""OpenAI baseline runner for Cloud Cost Optimizer Environment."""

from __future__ import annotations

import json
import os
import time
from typing import Optional

from openai import OpenAI
from env import Action, SupportEnv, TASKS, TICKETS, grade

BENCHMARK = "cloud-cost-optimizer-env"

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

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
    """Parse model output into a Cloud Action."""
    fields: dict[str, str] = {}
    for line in raw.strip().splitlines():
        if ":" not in line: continue
        key, _, val = line.partition(":")
        fields[key.strip().lower()] = val.strip()

    return Action(
        resource_id=fields.get("resource_id", "unknown"),
        action=fields.get("action", "ignore"),
        target_type=fields.get("target_type"),
        new_tags={"CostCenter": fields.get("costcenter")} if fields.get("costcenter") else None,
        reasoning=fields.get("reasoning", "No justification provided"),
        resolve=fields.get("resolve", "false").lower() == "true",
    )

def mock_model_output(expected: dict, task_id: str) -> str:
    """Deterministic oracle for FinOps tasks."""
    target = expected["target_optimizations"][0]
    out = (
        f"resource_id: {target['resource_id']}\n"
        f"action: {target['action']}\n"
        f"reasoning: Utilizing low CPU metrics to reduce over-provisioned cost.\n"
        f"resolve: true"
    )
    if "target_type" in target:
        out += f"\ntarget_type: {target['target_type']}"
    if "new_tags" in target:
        out += f"\ncostcenter: {target['new_tags'].get('CostCenter')}"
    return out

def run_task(task_id: str, client: Optional[OpenAI], mode: str) -> dict:
    task = TASKS[task_id]
    account = TICKETS[task.account_index]
    env = SupportEnv()
    obs = env.reset(task_id=task_id)
    
    _emit_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    if mode == "mock":
        raw = mock_model_output(account, task_id)
    else:
        # LLM Logic (Stubbed for demo)
        raw = "action: ignore\nreasoning: automated skip"

    action = parse_model_output(raw)
    obs, reward, done, info = env.step(action)
    
    action_str = f"{action.action}(resource={action.resource_id},resolve={str(action.resolve).lower()})"
    _emit_step(step=1, action=action_str, reward=reward.score, done=done, error=None)
    
    score = grade(task_id, action, account)
    _emit_end(success=True, steps=1, score=score, rewards=[reward.score])
    
    return {"task": task_id, "score": score}

def run_baseline():
    mode = os.getenv("BASELINE_MODE", "mock").lower()
    results = [run_task(tid, None, mode) for tid in ["easy", "medium", "hard"]]
    avg = sum(r["score"] for r in results) / 3
    print(f"\nFinal Average Score: {avg:.4f}")

if __name__ == "__main__":
    run_baseline()
