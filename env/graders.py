from __future__ import annotations

import difflib
from .models import Action

def grade(task_id: str, action: Action, expected_account: dict) -> float:
    """
    Grades a cloud optimization action based on cost saved and SLA safety.
    """
    targets = expected_account.get("target_optimizations", [])
    
    # 1. Resource Match
    target = next((t for t in targets if t["resource_id"] == action.resource_id), None)
    if not target:
        return 0.0 # Acted on wrong resource or irrelevant action

    # 2. Action Precision
    if action.action != target["action"]:
        return 0.2 # Recognized the resource but wrong strategy

    # 3. Task Specific Validation
    score = 0.5 # Base score for picking right resource/action
    
    if task_id == "easy":
        # Tagging check
        expected_tags = target.get("new_tags", {})
        if action.new_tags == expected_tags:
            score += 0.5
            
    elif task_id == "medium":
        # Stopping check (already verified by action type)
        score += 0.5
        
    elif task_id == "hard":
        # Multi-variable check: size + reasoning
        # Target size match
        if action.target_type == target["target_type"]:
            score += 0.3
        
        # Reasoning overlap (simple similarity check)
        sim = difflib.SequenceMatcher(None, action.reasoning.lower(), "over-provisioned resource utilization cost reduction").ratio()
        score += (sim * 0.2)
        
    return min(1.0, score)
