"""
Comprehensive test suite for the Mergington High School Activities API.

Tests cover GET /activities, POST /signup, and DELETE /unregister endpoints
with both success and error cases.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app


# ============================================================================
# GET /activities Endpoint Tests
# ============================================================================


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all available activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert len(activities) == 9
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Soccer Team" in activities


def test_get_activities_has_correct_structure(client):
    """Test that each activity has the required fields."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    for activity_name, activity in activities.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)


def test_get_activities_shows_participant_counts(client):
    """Test that participant lists are correctly populated."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    # Verify some activities have initial participants
    assert len(activities["Chess Club"]["participants"]) > 0
    assert len(activities["Programming Class"]["participants"]) > 0


# ============================================================================
# POST /activities/{activity_name}/signup Endpoint Tests
# ============================================================================


def test_signup_successful(client):
    """Test that a student can successfully sign up for an activity."""
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds the participant to the activity."""
    email = "testuser@mergington.edu"
    activity_name = "Drama Club"
    
    # Verify student is not in the activity initially
    activities_before = client.get("/activities").json()
    assert email not in activities_before[activity_name]["participants"]
    
    # Sign up for the activity
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    
    # Verify student is now in the activity
    activities_after = client.get("/activities").json()
    assert email in activities_after[activity_name]["participants"]


def test_signup_invalid_activity_returns_404(client):
    """Test that signing up for a non-existent activity returns 404."""
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate_returns_400(client):
    """Test that signing up twice returns a 400 error."""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


# ============================================================================
# DELETE /activities/{activity_name}/signup Endpoint Tests
# ============================================================================


def test_unregister_successful(client):
    """Test that a student can successfully unregister from an activity."""
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # First sign up
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant from the activity."""
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Sign up
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    # Verify student is in the activity
    activities_before = client.get("/activities").json()
    assert email in activities_before[activity_name]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    
    # Verify student is no longer in the activity
    activities_after = client.get("/activities").json()
    assert email not in activities_after[activity_name]["participants"]


def test_unregister_invalid_activity_returns_404(client):
    """Test that unregistering from a non-existent activity returns 404."""
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_non_existent_participant_returns_404(client):
    """Test that unregistering a student not in the activity returns 404."""
    email = "notinclub@mergington.edu"
    activity_name = "Chess Club"
    
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


# ============================================================================
# State Transition Tests
# ============================================================================


def test_multiple_participants_can_signup_to_activity(client):
    """Test that multiple different students can sign up for the same activity."""
    activity_name = "Art Club"
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    # Sign up all three students
    for email in emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        assert response.status_code == 200
    
    # Verify all are in the activity
    activities = client.get("/activities").json()
    for email in emails:
        assert email in activities[activity_name]["participants"]


def test_unregister_frees_up_slot_for_new_signup(client):
    """Test that after unregistering, a new student can take the slot."""
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    activity_name = "Science Olympiad"
    
    # Student 1 signs up
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email1},
    )
    assert response1.status_code == 200
    
    # Verify they're enrolled
    activities = client.get("/activities").json()
    assert email1 in activities[activity_name]["participants"]
    participant_count = len(activities[activity_name]["participants"])
    
    # Student 1 unregisters
    response_unregister = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email1},
    )
    assert response_unregister.status_code == 200
    
    # Verify they're removed and count decreased
    activities = client.get("/activities").json()
    assert email1 not in activities[activity_name]["participants"]
    new_count = len(activities[activity_name]["participants"])
    assert new_count == participant_count - 1
    
    # Student 2 can now sign up
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email2},
    )
    assert response2.status_code == 200
    
    # Verify Student 2 is now enrolled
    activities = client.get("/activities").json()
    assert email2 in activities[activity_name]["participants"]
