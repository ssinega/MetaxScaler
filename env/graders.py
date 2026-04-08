from __future__ import annotations

import difflib
from .models import Action

def grade(task_id: str, action: Action, expected_account: dict) -> float:
    """
    Grades a cloud optimization action based on cost saved and SLA safety.
    Implements robust validation for the Meta x Scaler Hackathon.
    """
    targets = expected_account.get("target_optimizations", [])
    
    # 1. Resource Match & Existence
    target = next((t for t in targets if t["resource_id"] == action.resource_id), None)
    if not target:
        # Penalize acting on non-existent or irrelevant resources
        return 0.0

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
    return round(min(1.0, final_score), 2)
