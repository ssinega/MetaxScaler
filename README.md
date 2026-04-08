# Cloud Infrastructure Cost Optimizer OpenEnv

An AI-powered environment for autonomous cloud cost management (FinOps). The agent monitors compute resource utilization and executes optimization strategies to reduce monthly bills while maintaining SLA compliance.

## 📖 Environment Overview

Enterprises lose billions annually to over-provisioned cloud resources. This environment simulates a cloud dashboard where an RL agent acts as a FinOps engineer.

- **Real-world utility**: Directly addresses the "Wasteful Cloud Spend" pain point.
- **Novel mechanics**: Dynamic resizing and governance-first tagging tasks.

## 🛠️ Action Space

| Field | Type | Description |
|---|---|---|
| `resource_id` | `string` | The target AWS/Azure resource ID |
| `action` | `string` | `resize`, `stop`, `terminate`, `tag`, `snapshot`, `ignore` |
| `target_type` | `string` | Required for `resize` (e.g., `t3.micro`) |
| `new_tags` | `dict` | Key-value pairs for governance tagging |
| `reasoning` | `string`| Justification for the change |

## 👁️ Observation Space

The agent monitors a dashboard of `Resources`:
- `resource_id`: Unique ID.
- `cpu_utilization`: Avg utilization %.
- `monthly_cost`: USD run rate.
- `tags`: Current cost centers.

## 🎯 Tasks

| Task | Difficulty | Goal |
|---|---|---|
| `easy` | Easy | Fix missing 'CostCenter' tags on untagged resources. |
| `medium` | Medium | Identify and shutdown compute nodes with <5% IDLE CPU. |
| `hard` | Hard | Downsize production nodes to minimal viable instance types. |

## 💰 Reward Function

The reward balances savings vs stability:
- **Cost Saved**: Direct positive reward for reducing monthly USD.
- **SLA Penalty**: Deduction if a resource is resized so small it exceeds 80% CPU utilization.
- **Efficiency Ratio**: Normalized score for how well the agent optimized the specific account.

## 🚀 Setup & Execution

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run server: `python main.py`
3. Run mock baseline: `BASELINE_MODE=mock python inference.py`
