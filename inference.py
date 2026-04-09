"""
Cloud Infrastructure Cost Optimizer - Final Inference Script
Strictly follows the Meta x Scaler Hackathon STDOUT format and logic requirements.
"""

import asyncio
import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI

# Domain Imports
from env import Action, SupportEnv, TASKS, ACCOUNTS, grade

# Mandatory Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
BASELINE_MODE = os.getenv("BASELINE_MODE", "api").lower().strip()

# Constants
BENCHMARK = "cloud-cost-optimizer-env"
MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.3 # Normalized score threshold

# Max possible reward calculation for normalization
# In our env, each correct action on a resource gives ~1.0 score.
# Hard task has 3 resources. Easy/Medium have 1.
MAX_TOTAL_REWARD = 3.0 

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

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

def mock_oracle(task_id: str, step: int, env: SupportEnv) -> str:
    """Deterministic oracle for FinOps tasks."""
    account = ACCOUNTS[TASKS[task_id].account_index]
    targets = account.get("target_optimizations", [])
    
    # Filter for targets not yet optimized
    remaining = [t for t in targets if t["resource_id"] not in env.optimized_resource_ids]
    if not remaining:
        return "action: ignore\nreasoning: All targets resolved.\nresolve: true"
    
    target = remaining[0]
    out = (
        f"resource_id: {target['resource_id']}\n"
        f"action: {target['action']}\n"
        f"reasoning: Utilization analysis confirms this resource is over-provisioned or misconfigured.\n"
        f"resolve: {'true' if len(remaining) == 1 else 'false'}"
    )
    if "target_type" in target:
        out += f"\ntarget_type: {target['target_type']}"
    if "new_tags" in target:
        out += f"\ncostcenter: {target['new_tags'].get('CostCenter', 'Engineering')}"
    return out

async def run_episode(task_id: str, client: OpenAI) -> float:
    env = SupportEnv()
    rewards: List[float] = []
    steps_taken = 0
    
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    obs = env.reset(task_id=task_id)
    done = False
    
    for step in range(1, MAX_STEPS + 1):
        if BASELINE_MODE == "mock":
            raw = mock_oracle(task_id, step, env)
        else:
            try:
                prompt = f"Observation: {obs.model_dump()}\nObjective: {TASKS[task_id].objective}\nOutput format: resource_id: <val>\naction: <val>\nreasoning: <val>\nresolve: <true/false>"
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = completion.choices[0].message.content or ""
            except Exception as e:
                log_step(step=step, action="error", reward=0.0, done=True, error=f"API error: {str(e)}")
                break

        try:
            action = parse_model_output(raw)
        except Exception as e:
            log_step(step=step, action="error", reward=0.0, done=True, error=f"Parse error: {str(e)}")
            break
        obs, reward_obj, done, info = env.step(action)
        
        step_reward = reward_obj.score
        rewards.append(step_reward)
        steps_taken = step
        
        action_desc = f"{action.action}(id={action.resource_id})"
        if action.target_type: action_desc += f"[target={action.target_type}]"
        
        log_step(step=step, action=action_desc, reward=step_reward, done=done, error=None)
        
        if done:
            break

    total_score = sum(rewards) / (len(ACCOUNTS[TASKS[task_id].account_index]["target_optimizations"]))
    total_score = min(max(total_score, 0.0), 1.0)
    success = total_score >= SUCCESS_SCORE_THRESHOLD
    
    log_end(success=success, steps=steps_taken, score=total_score, rewards=rewards)
    return total_score

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "sk-dummy")
    
    results = []
    for tid in ["easy", "medium", "hard"]:
        score = await run_episode(tid, client)
        results.append(score)
    
    avg = sum(results) / len(results)
    print(f"\nFinal Average Score: {avg:.4f}")
    
    # Write to final required artifact
    with open("baseline_scores.json", "w") as f:
        json.dump({
            "model": MODEL_NAME,
            "benchmark": BENCHMARK,
            "average_grader_score": avg
        }, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
