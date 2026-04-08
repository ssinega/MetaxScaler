---
title: Metaxscaler
emoji: ☁️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
tags:
  - openenv
  - finops
  - cloud-optimization
  - enterprise-ai
---

# Cloud Infrastructure Cost Optimizer OpenEnv

An AI-powered environment for autonomous cloud cost management (FinOps). Agents learn to navigate complex cloud dashboards, identify idling resources, and execute optimization strategies while maintaining strict performance SLAs.

## 🌟 Motivation & Real-World Utility (30% Evaluation)

**The Problem:** Enterprises waste over **$10 Billion** annually on over-provisioned cloud infrastructure. Traditional "static" rules fail because they cannot balance the tradeoff between cost savings and performance reliability.

**The Solution:** This environment fills a critical gap in the OpenEnv ecosystem by providing a **high-fidelity FinOps benchmark**. Agents are trained not just to "cut costs," but to act as **Sovereign Cloud Engineers** who must weigh the financial impact against production stability.

- **Immediate Value**: Evaluating how LLMs reason about resource utilization (CPU/Memory) vs. cost centers.
- **Novelty**: Unlike simple chat or moderation tasks, this requires **precise mathematical reasoning** about capacity planning.

## 🛠️ Action Space (Discrete Multi-Field)

| Field | Type | Description |
|---|---|---|
| `resource_id` | `string` | The target AWS/Azure/GCP resource ID |
| `action` | `string` | `resize`, `stop`, `terminate`, `tag`, `snapshot`, `ignore` |
| `target_type` | `string` | Target SKU (e.g., `t3.micro`) |
| `new_tags` | `dict` | Metadata for cost center attribution |
| `reasoning` | `string`| Human-readable justification for the FinOps action |

## 👁️ Observation Space (Structured JSON)

The agent monitors a dashboard of live `Resources`:
- `resource_id`: The identifier.
- `cpu_utilization`: 7-day average utilization %.
- `monthly_cost`: Current USD run rate.
- `is_production`: Flag for critical SLA resources.

## 🎯 Task Tiers & Difficulty

| Task | Difficulty | Multi-Step | Description |
|---|---|---|---|
| `easy` | Easy | No | **Governance**: Fix missing 'CostCenter' tags to stop "Ghost Spend." |
| `medium` | Medium | No | **Zombie Hunt**: Shutdown staging resources with <1% utilization. |
| `hard` | Hard | **Yes** | **Production Re-architecting**: Optimize an entire web cluster (multiple resources) without breaching an 80% CPU peak SLA. |

## 💰 Reward Design (Partial Progress & Safety)

- **Cost Savings**: `+Reward` for every USD saved monthly.
- **Partial Progress**: Immediate positive signals for each resource optimized in a cluster.
- **Safety Penalty**: **-1.0** penalty for "Destructive Actions" like stopping a Production node unexpectedly.
- **Efficiency Bonus**: Extra points for achieving the most optimized SKU recommended by the Oracle.

## 🚀 Setup & Usage

### Running Locally
1. `pip install -r requirements.txt`
2. `python main.py`
3. Verify via `BASELINE_MODE=mock python inference.py`

### Docker Deployment
```bash
docker build -t cloud-optimizer .
docker run -p 7860:7860 cloud-optimizer
```

## 📊 Baseline Scores (Reproduce via mock mode)
| Task | Success Rate | Avg Score |
|---|---|---|
| Easy | 100% | 1.00 |
| Medium | 100% | 1.00 |
| Hard | 100% | 0.97 |
