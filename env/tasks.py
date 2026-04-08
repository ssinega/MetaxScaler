from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Task model
# ---------------------------------------------------------------------------

class Task(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    difficulty: Literal["easy", "medium", "hard"]
    objective: str = Field(..., description="The main goal for the agent")
    description: str = Field(..., description="Detailed instructions and SLA constraints")
    scored_fields: list[str] = Field(..., description="Action fields that drive the reward")
    account_index: int = Field(default=0, description="Index into the ACCOUNTS dataset")
    sla_constraint: float = Field(default=0.0, description="Minimum CPU utilization allowed for production")

# ---------------------------------------------------------------------------
# Task catalogue
# ---------------------------------------------------------------------------

TASKS: dict[str, Task] = {
    "easy": Task(
        task_id="easy",
        difficulty="easy",
        objective="Ensure all resources are properly tagged for cost center attribution.",
        description=(
            "Your goal is to identify untagged resources and apply the correct 'CostCenter' tag. "
            "For account ACC-003, identify the untagged instance and tag it with 'CostCenter: Engineering'."
        ),
        scored_fields=["action", "new_tags"],
        account_index=2, # ACC-003
    ),

    "medium": Task(
        task_id="medium",
        difficulty="medium",
        objective="Identify and stop resources that are idling to stay within budget.",
        description=(
            "Account ACC-001 is over budget. Identify resources with <5% CPU usage "
            "and stop them to immediately reduce daily run rate."
        ),
        scored_fields=["action", "resource_id"],
        account_index=0, # ACC-001
    ),

    "hard": Task(
        task_id="hard",
        difficulty="hard",
        objective="Right-size production infrastructure to maximize efficiency without breaching SLAs.",
        description=(
            "Account ACC-002 has high spend. You must resize production instances to the smallest "
            "available type that can still handle the detected peak workload. "
            "SLA: Average CPU must not exceed 80% after resizing."
        ),
        scored_fields=["action", "resource_id", "target_type", "reasoning"],
        account_index=1, # ACC-002
        sla_constraint=80.0
    ),
}
