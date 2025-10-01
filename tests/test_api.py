"""Tests for the NeuroGym API module."""

import sys
from pathlib import Path

import pytest

# Check if fastapi is available
try:
    import fastapi
    import uvicorn
    from pydantic import BaseModel

    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_api_module_import():
    """Test that the API module can be imported."""
    from neurogym.api import main

    assert main is not None


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_api_app_creation():
    """Test that the FastAPI app is created correctly."""
    from neurogym.api.main import app

    assert app is not None
    assert app.title == "NeuroGym API"


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_api_routes_exist():
    """Test that expected routes are registered."""
    from neurogym.api.main import app

    routes = [route.path for route in app.routes]

    # Check for expected endpoints
    assert "/" in routes
    assert "/health" in routes
    assert "/tasks" in routes
    assert "/environments" in routes


@pytest.mark.skipif(not _FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_pydantic_models():
    """Test that Pydantic models are defined correctly."""
    from neurogym.api.main import (
        ActionRequest,
        EnvironmentConfig,
        EnvironmentInfo,
        ResetResponse,
        StepResponse,
    )

    # Test EnvironmentConfig
    config = EnvironmentConfig(
        task_name="PerceptualDecisionMaking-v0", kwargs={"dt": 100}
    )
    assert config.task_name == "PerceptualDecisionMaking-v0"
    assert config.kwargs == {"dt": 100}

    # Test ActionRequest
    action_req = ActionRequest(session_id="test-id", action=1)
    assert action_req.session_id == "test-id"
    assert action_req.action == 1


# Test that can be run without FastAPI
def test_api_directory_exists():
    """Test that the API directory exists."""
    import neurogym

    api_path = Path(neurogym.__file__).parent / "api"
    assert api_path.exists()
    assert api_path.is_dir()


def test_api_main_file_exists():
    """Test that the main.py file exists in the API directory."""
    import neurogym

    main_file = Path(neurogym.__file__).parent / "api" / "main.py"
    assert main_file.exists()
    assert main_file.is_file()
