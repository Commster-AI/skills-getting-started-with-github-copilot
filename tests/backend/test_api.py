from fastapi.testclient import TestClient

import pytest

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    """Restore the in-memory activities after each test."""
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }

    yield

    for name, details in activities.items():
        details["participants"] = list(original_participants[name])


def test_root_redirects_to_static_index():
    # Arrange
    # No special setup required for the root route.

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data():
    # Arrange
    # The in-memory activities dictionary is seeded by the app.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"]


def test_signup_adds_new_student_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "copilot-test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_returns_404_for_unknown_activity():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
