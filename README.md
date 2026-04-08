# Support Ticket OpenEnv

AI environment for the Meta x Scaler Hackathon simulating an enterprise customer support ticket resolution flow.

## 📖 Environment Overview

This environment mimics a B2B SaaS support helpdesk. An RL agent acts as a triage specialist that must read incoming tickets, categorize them, set priorities, and either guide the user or escalate critical issues.

- **Real-world utility**: Addresses the enterprise pain point of ticket mis-triage and SLA breaches.
- **Novel mechanics**: Includes compound ticket detection where multiple issues must be identified to trigger an escalation score.

## 🛠️ Action Space

The model must produce a JSON-compatible structured action:

| Field | Type | Description |
|---|---|---|
| `category` | `string` | One of: `billing`, `account`, `technical` |
| `priority` | `string` | One of: `low`, `medium`, `high` |
| `action` | `string` | One of: `refund`, `escalate`, `guide` |
| `response` | `string` | Empathetic natural language response |
| `resolve` | `boolean` | Set to `true` to close the ticket |

## 👁️ Observation Space

The agent receives the following structured observation:

- `ticket_id`: Unique identifier for the current ticket.
- `user_query`: The customer's message.
- `conversation_history`: List of prior interactions in the episode.
- `available_categories`: List of valid categories.
- `available_priorities`: List of valid priorities.
- `available_actions`: List of valid resolution actions.

## 🎯 Tasks

| Task | Difficulty | Objective |
|---|---|---|
| `easy` | Easy | Correctly identify the ticket category. |
| `medium` | Medium | Identify both the category and the priority level. |
| `hard` | Hard | Full resolution: category, priority, action, and keyword-rich response. |

## 💰 Reward Function

The reward is a combination of:
1. **Progress Bonus**: Given for each step that brings the state closer to resolution.
2. **Success Score**: Grader score (0.0 to 1.0) on resolution.
3. **Step Cost**: Small penalty (-0.01) per step to encourage efficiency.
4. **Stagnation Penalty**: Penalty if the agent repeats actions or fails to progress.
5. **Premature Resolve Penalty**: Heavy penalty if `resolve=true` is set before proper triage (especially in hard mode).

## 🚀 Setup & Execution

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run smoke test: `python main.py`
3. Run inference: `BASELINE_MODE=mock python inference.py`

### Docker Execution
```bash
docker build -t support-ticket-env .
docker run -p 7860:7860 support-ticket-env
```

## 📊 Baseline Scores

Scores from `BASELINE_MODE=mock` (oracle runner):

| Task   | Grader Score | Episode Return | Steps |
|--------|-------------:|---------------:|------:|
| easy   |       0.99   |         0.99   |     1 |
| medium |       0.99   |         0.95   |     1 |
| hard   |       0.79   |         1.12   |     2 |
| **Avg**| **0.9233**   | — | — |

## 🤖 Running Inference

To run against a live model:
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="your_token_here"
python inference.py
```
