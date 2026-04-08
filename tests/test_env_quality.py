"""Full quality test suite for SupportEnv."""
import pytest
from env import SupportEnv, Action, TASKS, TICKETS, grade

# Helper
def _make_action(category="technical", priority="high", action="escalate",
                 response="We will escalate this to our specialist team urgently.",
                 resolve=True):
    return Action(category=category, priority=priority, action=action,
                  response=response, resolve=resolve)

# 1. Grader determinism — same input always gives same score
def test_grader_determinism():
    action = _make_action()
    expected = TICKETS[0]
    s1 = grade("hard", action, expected)
    s2 = grade("hard", action, expected)
    assert s1 == s2, "Grader must be deterministic"

# 2. Grader output bounds for all difficulties
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_grader_bounds(difficulty):
    action = _make_action()
    for ticket in TICKETS:
        score = grade(difficulty, action, ticket)
        assert 0.0 < score < 1.0, f"Score {score} out of open interval (0,1) for {difficulty}"

# 3. Hard-mode premature resolve penalty
def test_premature_resolve_penalty():
    env = SupportEnv()
    env.reset(task_id="hard")
    action = _make_action(resolve=True)
    _, reward, _, _ = env.step(action)
    assert reward.score < 1.0
    assert "premature" in (reward.reason or "").lower()

# 4. Trajectory reward varies across steps (non-static)
def test_trajectory_shaping_variability():
    env = SupportEnv()
    env.reset(task_id="hard")
    scores = []
    for i in range(3):
        resolve = i >= 1
        _, r, done, _ = env.step(_make_action(resolve=resolve))
        scores.append(r.score)
        if done:
            break
    assert len(set(scores)) > 1 or len(scores) == 1, "Rewards must vary or episode ends early"

# 5. Compound-ticket under-triage penalty
def test_compound_undertriage_penalty():
    env = SupportEnv()
    env.reset(task_id="hard", ticket_index=16)  # compound ticket (updated index for new dataset)
    action = _make_action(action="guide", resolve=False)
    _, reward, _, _ = env.step(action)
    assert "compound" in (reward.reason or "").lower() or reward.score < 0.9

# 6. Close method exists and is callable
def test_close_method():
    env = SupportEnv()
    env.reset()
    env.close()  # should not raise

# 7. Render method works
def test_render_method():
    env = SupportEnv()
    env.reset()
    rendered = env.render()
    assert isinstance(rendered, str)
    assert len(rendered) > 0

# 8. Max steps terminates episode
def test_max_steps_termination():
    env = SupportEnv()
    env.reset(task_id="easy")
    done = False
    steps = 0
    while not done:
        _, _, done, info = env.step(_make_action(resolve=False))
        steps += 1
        if steps > 10:
            break
    assert done, "Episode should terminate at MAX_STEPS"

# 9. State dict contains expected keys
def test_state_keys():
    env = SupportEnv()
    env.reset()
    s = env.state()
    for key in ("ticket_id", "step", "max_steps", "done", "task_id"):
        assert key in s

# 10. Available action space in observation
def test_observation_action_space():
    env = SupportEnv()
    obs = env.reset()
    assert hasattr(obs, "available_categories")
    assert "billing" in obs.available_categories
    assert "escalate" in obs.available_actions

# 11. Unknown task_id raises ValueError
def test_unknown_task_raises():
    env = SupportEnv()
    with pytest.raises(ValueError):
        env.reset(task_id="impossible")

# 12. Step on done env raises RuntimeError
def test_step_on_done_raises():
    env = SupportEnv()
    env.reset(task_id="easy")
    env.step(_make_action(resolve=True))
    with pytest.raises(RuntimeError):
        env.step(_make_action(resolve=True))

# 13. All 3 tasks run end-to-end without error
@pytest.mark.parametrize("task_id", ["easy", "medium", "hard"])
def test_all_tasks_run(task_id):
    env = SupportEnv()
    obs = env.reset(task_id=task_id)
    assert obs.ticket_id is not None
    action = _make_action()
    obs2, reward, done, info = env.step(action)
    assert 0.0 <= reward.score <= 1.0
    assert "task_id" in info


# GAP-13: Additional tests for full coverage

# Test: close() method exists and is callable
def test_close_method_exists():
    env = SupportEnv()
    env.reset()
    assert hasattr(env, "close")
    env.close()  # must not raise

# Test: step() on closed env raises RuntimeError
def test_step_after_close_raises():
    env = SupportEnv()
    env.reset(task_id="easy")
    # Resolve and mark done
    from env import Action
    action = Action(category="technical", priority="low", action="guide",
                    response="Here are the steps.", resolve=True)
    env.step(action)
    try:
        env.step(action)
        assert False, "Expected RuntimeError on step after done"
    except RuntimeError:
        pass

# Test: state() returns expected keys
def test_state_returns_required_keys():
    env = SupportEnv()
    env.reset(task_id="medium")
    s = env.state()
    for key in ("ticket_id", "step", "max_steps", "done", "task_id"):
        assert key in s, f"state() missing key: {key}"

# Test: reset() with unknown task_id raises ValueError
def test_reset_unknown_task_raises():
    env = SupportEnv()
    try:
        env.reset(task_id="nonexistent")
        assert False, "Expected ValueError"
    except ValueError:
        pass

# Test: all 3 tasks run without error end-to-end
def test_all_tasks_run_end_to_end():
    from env import Action
    for task_id in ["easy", "medium", "hard"]:
        env = SupportEnv()
        obs = env.reset(task_id=task_id)
        assert obs.ticket_id is not None
        action = Action(
            category="technical", priority="high", action="escalate",
            response="We escalated this issue to our specialist team.",
            resolve=True,
        )
        obs2, reward, done, info = env.step(action)
        assert 0.0 <= reward.score <= 1.0
        assert "task_id" in info
        env.close()

# Test: episode terminates at MAX_STEPS without resolve
def test_max_steps_terminates_episode():
    from env import Action
    env = SupportEnv()
    env.reset(task_id="easy")
    done = False
    steps = 0
    action = Action(category="billing", priority="low", action="guide",
                    response="Here is how.", resolve=False)
    while not done:
        _, _, done, _ = env.step(action)
        steps += 1
        if steps > 20:
            break
    assert done, "Episode must terminate at MAX_STEPS"

# Test: graders return open-interval scores for all tasks and tickets
def test_grader_open_interval_all_tickets():
    from env import Action, TICKETS, grade
    action = Action(category="technical", priority="high", action="escalate",
                    response="Escalating to specialist team.", resolve=True)
    for difficulty in ["easy", "medium", "hard"]:
        for ticket in TICKETS:
            score = grade(difficulty, action, ticket)
            assert 0.0 < score < 1.0, \
                f"Score {score} out of (0,1) for difficulty={difficulty} ticket={ticket['id']}"
