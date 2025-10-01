"""
FastAPI web service for NeuroGym environments.

This module provides a REST API to interact with NeuroGym environments,
enabling web-based access to neuroscience tasks.
"""

from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import neurogym as ngym


def convert_numpy(obj: Any) -> Any:
    """Convert numpy types to Python native types."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Initialize FastAPI app
app = FastAPI(
    title="NeuroGym API",
    description="REST API for NeuroGym neuroscience task environments",
    version="1.0.0",
)

# Store active environment sessions
active_envs: Dict[str, Any] = {}


class EnvironmentConfig(BaseModel):
    """Configuration for creating an environment."""

    task_name: str = Field(..., description="Name of the task environment")
    kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters for the environment"
    )


class ActionRequest(BaseModel):
    """Request model for taking an action."""

    session_id: str = Field(..., description="Session ID of the environment")
    action: int = Field(..., description="Action to take")


class StepResponse(BaseModel):
    """Response model for step results."""

    observation: List[float] = Field(..., description="Environment observation")
    reward: float = Field(..., description="Reward from the action")
    terminated: bool = Field(..., description="Whether episode has terminated")
    truncated: bool = Field(..., description="Whether episode was truncated")
    info: Dict[str, Any] = Field(..., description="Additional information")


class ResetResponse(BaseModel):
    """Response model for reset results."""

    observation: List[float] = Field(..., description="Initial observation")
    info: Dict[str, Any] = Field(..., description="Additional information")


class EnvironmentInfo(BaseModel):
    """Information about an environment."""

    session_id: str
    task_name: str
    observation_space: Dict[str, Any]
    action_space: Dict[str, Any]


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "NeuroGym API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/tasks")
async def list_tasks() -> Dict[str, List[str]]:
    """List all available tasks."""
    try:
        # Get all registered environments
        all_tasks = ngym.envs.registration.ALL_ENVS.keys()
        return {"tasks": sorted(list(all_tasks))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")


@app.post("/environments", response_model=EnvironmentInfo)
async def create_environment(config: EnvironmentConfig) -> EnvironmentInfo:
    """Create a new environment instance."""
    try:
        # Create environment
        env = ngym.make(config.task_name, **config.kwargs)

        # Generate session ID
        import uuid

        session_id = str(uuid.uuid4())

        # Store environment
        active_envs[session_id] = {
            "env": env,
            "task_name": config.task_name,
        }

        # Get space information
        obs_space = env.observation_space
        act_space = env.action_space

        return EnvironmentInfo(
            session_id=session_id,
            task_name=config.task_name,
            observation_space={
                "shape": [int(x) for x in obs_space.shape],
                "dtype": str(obs_space.dtype),
            },
            action_space={
                "n": int(act_space.n) if hasattr(act_space, "n") else None,
                "shape": [int(x) for x in getattr(act_space, "shape", [])],
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error creating environment: {str(e)}"
        )


@app.post("/environments/{session_id}/reset", response_model=ResetResponse)
async def reset_environment(session_id: str) -> ResetResponse:
    """Reset an environment."""
    if session_id not in active_envs:
        raise HTTPException(status_code=404, detail="Environment not found")

    try:
        env = active_envs[session_id]["env"]
        obs, info = env.reset()

        return ResetResponse(
            observation=obs.flatten().tolist(),
            info=info if isinstance(info, dict) else {},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error resetting environment: {str(e)}"
        )


@app.post("/environments/{session_id}/step", response_model=StepResponse)
async def step_environment(session_id: str, action_req: ActionRequest) -> StepResponse:
    """Take a step in the environment."""
    if session_id not in active_envs:
        raise HTTPException(status_code=404, detail="Environment not found")

    try:
        env = active_envs[session_id]["env"]
        obs, reward, terminated, truncated, info = env.step(action_req.action)

        return StepResponse(
            observation=obs.flatten().tolist(),
            reward=float(reward),
            terminated=bool(terminated),
            truncated=bool(truncated),
            info={k: convert_numpy(v) for k, v in info.items()} if isinstance(info, dict) else {},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error stepping environment: {str(e)}"
        )


@app.delete("/environments/{session_id}")
async def delete_environment(session_id: str) -> Dict[str, str]:
    """Delete an environment instance."""
    if session_id not in active_envs:
        raise HTTPException(status_code=404, detail="Environment not found")

    try:
        env = active_envs[session_id]["env"]
        env.close()
        del active_envs[session_id]
        return {"message": "Environment deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting environment: {str(e)}"
        )


@app.get("/environments")
async def list_environments() -> Dict[str, List[Dict[str, str]]]:
    """List all active environment sessions."""
    sessions = [
        {"session_id": sid, "task_name": data["task_name"]}
        for sid, data in active_envs.items()
    ]
    return {"sessions": sessions}


@app.get("/environments/{session_id}")
async def get_environment_info(session_id: str) -> EnvironmentInfo:
    """Get information about a specific environment."""
    if session_id not in active_envs:
        raise HTTPException(status_code=404, detail="Environment not found")

    try:
        env = active_envs[session_id]["env"]
        task_name = active_envs[session_id]["task_name"]

        obs_space = env.observation_space
        act_space = env.action_space

        return EnvironmentInfo(
            session_id=session_id,
            task_name=task_name,
            observation_space={
                "shape": [int(x) for x in obs_space.shape],
                "dtype": str(obs_space.dtype),
            },
            action_space={
                "n": int(act_space.n) if hasattr(act_space, "n") else None,
                "shape": [int(x) for x in getattr(act_space, "shape", [])],
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting environment info: {str(e)}"
        )
