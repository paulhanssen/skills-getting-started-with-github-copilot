from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_from_activity():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == (
        f"Unregistered {email} from {activity_name}"
    )

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
