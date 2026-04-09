from __future__ import annotations

import difflib
from .models import Action


def _strict_unit_score(value: float, default: float = 0.01) -> float:
    """Return a finite score guaranteed to be in the open interval (0, 1)."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = default

    if score != score:  # NaN check without importing math
        score = default

    return max(0.01, min(0.99, round(score, 2)))

def grade(task_id: str, action: Action, expected_account: dict) -> float:
    """
    Grades a cloud optimization action based on cost saved and SLA safety.
    Implements robust validation for the Meta x Scaler Hackathon.
    """
    targets = expected_account.get("target_optimizations", [])
    
    # 1. Resource Match & Existence
    target = next((t for t in targets if t["resource_id"] == action.resource_id), None)
    
    # SAFETY CHECK: Heavy penalty for destructive actions on PRODUCTION resources
    # that are not part of our optimization targets.
    affected_resource = next((r for r in expected_account["resources"] if r["resource_id"] == action.resource_id), None)
    if affected_resource and affected_resource.get("is_production") and action.action in ["stop", "terminate"]:
        if not target or target["action"] not in ["stop", "terminate"]:
            return 0.01 # Immediate negative signal for destructive production behavior

    if not target:
        return 0.05 # Acted on wrong resource or irrelevant action

    # 2. Strategy Alignment
    # Determine how close the action is to the recommended strategy
    strategy_score = 0.0
    if action.action == target["action"]:
        strategy_score = 0.6
    elif action.action in ["stop", "terminate"] and target["action"] in ["stop", "terminate"]:
        strategy_score = 0.4 # Directionally correct (deletion/stop)
    else:
        return 0.1 # Wrong strategy entirely

    # 3. Parameter Precision (Optimization Level)
    param_score = 0.0
    if task_id == "easy":
        expected_tags = target.get("new_tags", {})
        # Case-insensitive tag matching
        actual_tags = {k.lower(): v.lower() for k, v in (action.new_tags or {}).items()}
        normalized_expected = {k.lower(): v.lower() for k, v in expected_tags.items()}
        if all(actual_tags.get(k) == v for k, v in normalized_expected.items()):
            param_score = 0.4
            
    elif task_id == "medium":
        # Strategy alone is sufficient for stopping idle nodes
        param_score = 0.4
        
    elif task_id == "hard":
        # Check target instance type and reasoning
        if action.target_type == target.get("target_type"):
            param_score += 0.2
        
        # Fuzzy Reasoning Match: Detect key terms like 'over-provisioned' or 'cost'
        keywords = ["cpu", "utilization", "over-provisioned", "cost", "save", "idle", "performance"]
        matches = sum(1 for word in keywords if word in action.reasoning.lower())
        param_score += min(0.2, (matches / len(keywords)) * 0.4)
        
    final_score = strategy_score + param_score
    return _strict_unit_score(final_score)
