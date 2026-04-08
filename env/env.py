from __future__ import annotations

from typing import Any, Tuple
import datetime

from .models import Action, Observation, Reward, Resource
from .tasks import TASKS
from .dataset import ACCOUNTS
from .graders import grade

class SupportEnv:
    """
    Cloud Infrastructure Cost Optimizer Environment.
    An agent monitors resource telemetry and takes actions to minimize spend.
    Supports partial progress tracking for multi-step tasks.
    """
    def __init__(self):
        self.current_account: dict = {}
        self.current_task_id: str | None = None
        self.step_count = 0
        self.max_steps = 10
        self.done = False
        self.optimized_resource_ids: set[str] = set()

    def reset(self, ticket_index: int = 0, task_id: str | None = None) -> Observation:
        """Resets the environment with fresh state tracking."""
        if task_id and task_id in TASKS:
            self.current_task_id = task_id
            self.current_account = ACCOUNTS[TASKS[task_id].account_index]
        else:
            self.current_task_id = "easy"
            self.current_account = ACCOUNTS[ticket_index % len(ACCOUNTS)]
            
        self.step_count = 0
        self.done = False
        self.optimized_resource_ids = set()
        return self.state()

    def state(self) -> Observation:
        """Constructs the current observation from the underlying infrastructure state."""
        resources = []
        for r_dict in self.current_account["resources"]:
            # In a true persistent simulation, we would mutate the resource dict
            # For this benchmark, we simulate the state based on optimized_resource_ids
            r = Resource(**r_dict)
            if r.resource_id in self.optimized_resource_ids:
                # Mock the effect of optimization
                r.monthly_cost *= 0.5 
                r.tags["OptimizedBy"] = "AI_Agent"
            resources.append(r)

        return Observation(
            account_id=self.current_account["id"],
            resources=resources,
            monthly_budget=self.current_account["monthly_budget"],
            current_spend=self.current_account["current_spend"],
            timestamp=datetime.datetime.now().isoformat()
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict[str, Any]]:
        """
        Executes an optimization action.
        Provides high-fidelity rewards with partial progress signals.
        """
        if self.done:
            raise RuntimeError("Episode finished. Call reset().")

        self.step_count += 1
        
        # 1. Evaluate specific action accuracy (0.0 to 1.0)
        action_quality = grade(self.current_task_id or "easy", action, self.current_account)
        
        # 2. Check for duplicate actions (Stagnation Penalty)
        is_duplicate = action.resource_id in self.optimized_resource_ids
        
        # 3. Calculate Reward
        # Base: Quality * CostImpact
        # Partial Progress: Reward uniquely correct actions
        reward_score = 0.0
        cost_saved = 0.0
        
        if action_quality > 0.5 and not is_duplicate:
            self.optimized_resource_ids.add(action.resource_id)
            reward_score = action_quality
            cost_saved = action_quality * 100.0 # Mocked savings impact
        elif is_duplicate:
            reward_score = -0.1 # Penalty for repeating actions
        else:
            reward_score = 0.0 # Wrong action

        reward = Reward(
            score=reward_score,
            cost_reduction=cost_saved,
            entropy_bonus=0.01 if not is_duplicate else 0.0
        )

        # 4. Termination Logic
        targets = self.current_account.get("target_optimizations", [])
        all_fixed = all(t["resource_id"] in self.optimized_resource_ids for t in targets)
        
        if action.resolve or all_fixed or self.step_count >= self.max_steps:
            self.done = True

        return self.state(), reward, self.done, {
            "message": "Step processed.",
            "progress": f"{len(self.optimized_resource_ids)}/{len(targets)} resources optimized"
        }

    def render(self):
        """Standard OpenEnv render method."""
        print(f"Cloud Stats: {len(self.optimized_resource_ids)} optimized.")

    def close(self):
        """Cleanup logic."""
        pass
