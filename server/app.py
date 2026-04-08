"""FastAPI app for the Cloud Optimizer OpenEnv."""

from __future__ import annotations

from typing import Optional
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field

from env import Action, SupportEnv, TASKS, TICKETS, grade

app = FastAPI(title="cloud-optimizer-env", version="0.1.0")
RUNTIME_ENV = SupportEnv()

class ResetRequest(BaseModel):
    task_id: Optional[str] = Field(default=None, description="One of: easy, medium, hard")
    ticket_index: int = Field(default=0, description="Fallback index for ACCOUNTS dataset")

class StepRequest(BaseModel):
    action: Action

@app.get("/")
def root():
    return {"name": "cloud-optimizer-env", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset(req: ResetRequest = Body(default=ResetRequest())):
    obs = RUNTIME_ENV.reset(ticket_index=req.ticket_index, task_id=req.task_id)
    return {"observation": obs.model_dump(), "state": RUNTIME_ENV.state().model_dump()}

@app.post("/step")
def step(req: StepRequest):
    obs, reward, done, info = RUNTIME_ENV.step(req.action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    }

import uvicorn

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": {
            tid: {
                "difficulty": t.difficulty,
                "objective": t.objective,
                "description": t.description
            }
            for tid, t in TASKS.items()
        }
    }

def main():
    """Main entry point for automated deployment."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()

# End of file
