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
    Simulates a cloud dashboard where an agent takes actions to reduce spend.
    """
    def __init__(self):
        self.current_account: dict = {}
        self.current_task_id: str | None = None
        self.step_count = 0
        self.max_steps = 5
        self.done = False

    def reset(self, ticket_index: int = 0, task_id: str | None = None) -> Observation:
        """Resets the environment to a specific cloud account scenario."""
        if task_id and task_id in TASKS:
            self.current_task_id = task_id
            self.current_account = ACCOUNTS[TASKS[task_id].account_index]
        else:
            self.current_task_id = "easy"
            self.current_account = ACCOUNTS[ticket_index % len(ACCOUNTS)]
            
        self.step_count = 0
        self.done = False
        return self.state()

    def state(self) -> Observation:
        """Returns the current structured observation of the account."""
        resources = [Resource(**r) for r in self.current_account["resources"]]
        return Observation(
            account_id=self.current_account["id"],
            resources=resources,
            monthly_budget=self.current_account["monthly_budget"],
            current_spend=self.current_account["current_spend"],
            timestamp=datetime.datetime.now().isoformat()
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict[str, Any]]:
        """Applies an optimization action and returns the feedback loop."""
        if self.done:
            raise RuntimeError("Episode already finished. Call reset().")

        self.step_count += 1
        
        # Calculate Reward using the grader
        score = grade(self.current_task_id or "easy", action, self.current_account)
        
        # Simulate cost reduction for the reward model
        # (In a real env, we'd mutate self.current_account resources)
        reward = Reward(
            score=score,
            cost_reduction=score * 50.0, # Mocked savings
            penalty=0.0 if score > 0.5 else 0.1,
            efficiency_ratio=score * 0.2
        )

        if action.resolve or self.step_count >= self.max_steps:
            self.done = True

        return self.state(), reward, self.done, {"message": "Action processed."}

    def close(self):
        """Cleanup logic."""
        pass
