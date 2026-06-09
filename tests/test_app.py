from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_removes_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    original_participants = list(activities[activity_name]["participants"])

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_participant_fails_for_unknown_student():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    original_participants = list(activities[activity_name]["participants"])

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}
    finally:
        activities[activity_name]["participants"] = original_participants
