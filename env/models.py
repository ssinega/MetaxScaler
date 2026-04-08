from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Observation: What the agent sees (Cloud Resources & Metrics)
# ---------------------------------------------------------------------------

class Resource(BaseModel):
    resource_id: str = Field(..., description="Unique AWS/Azure resource identifier")
    resource_type: str = Field(..., description="e.g., m5.large, db.t3.medium")
    cpu_utilization: float = Field(..., description="Average CPU utilization % over 7 days")
    memory_utilization: float = Field(..., description="Average Memory utilization % over 7 days")
    monthly_cost: float = Field(..., description="Estimated cost per month in USD")
    tags: dict[str, str] = Field(default_factory=dict, description="Resource tags (CostCenter, Owner, etc.)")
    is_production: bool = Field(default=False, description="Whether this is a performance-critical resource")

class Observation(BaseModel):
    account_id: str = Field(..., description="Virtual cloud account identifier")
    resources: list[Resource] = Field(default_factory=list, description="List of cloud resources to optimize")
    monthly_budget: float = Field(..., description="Monthly cost threshold in USD")
    current_spend: float = Field(..., description="Total spend so far this month")
    timestamp: str = Field(..., description="Observation timestamp")

# ---------------------------------------------------------------------------
# Action: What the agent does (Optimization Decisions)
# ---------------------------------------------------------------------------

class Action(BaseModel):
    resource_id: str = Field(..., description="The ID of the resource to act upon")
    action: Literal["resize", "stop", "terminate", "tag", "snapshot", "ignore"] = Field(
        ..., 
        description="Optimization action to take"
    )
    target_type: Optional[str] = Field(
        None, 
        description="Required for 'resize': e.g., 't3.micro'"
    )
    new_tags: Optional[dict[str, str]] = Field(
        None, 
        description="Required for 'tag': Key-value pairs to apply"
    )
    reasoning: str = Field(..., description="Brief justification for the action")
    resolve: bool = Field(
        default=False, 
        description="Set to true when all optimization tasks for this session are complete"
    )

# ---------------------------------------------------------------------------
# Reward: How the agent is scored
# ---------------------------------------------------------------------------

class Reward(BaseModel):
    score: float = Field(default=0.0, description="Normalized score [0, 1]")
    cost_reduction: float = Field(default=0.0, description="Actual monthly USD saved by this action")
    penalty: float = Field(default=0.0, description="Deduction for performance risks or SLA breaches")
    efficiency_ratio: float = Field(default=0.0, description="Cost saved relative to original spend")
