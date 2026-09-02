"""
Pytest configuration and fixtures for FastAPI tests.

This module provides reusable fixtures for test isolation and client setup.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def activities_backup():
    """Create a backup of the initial activities state."""
    return {
        activity_name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy(),
        }
        for activity_name, activity in activities.items()
    }


@pytest.fixture(autouse=True)
def reset_state(activities_backup):
    """
    Reset activities state before and after each test to ensure test isolation.
    
    This fixture runs automatically (autouse=True) before and after each test,
    restoring the in-memory activities dictionary to its initial state.
    """
    yield
    # After test runs, restore the original state
    for activity_name in activities:
        activities[activity_name]["participants"] = activities_backup[activity_name]["participants"].copy()
