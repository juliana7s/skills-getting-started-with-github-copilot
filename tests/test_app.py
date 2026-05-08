"""API tests for Mergington High School activities."""

import os
import sys

from fastapi.testclient import TestClient

# Ensure the app package can be imported from src/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import app  # noqa: E402

client = TestClient(app)


def test_root_redirect():
    # Arrange
    url = "/"
    expected_location = "/static/index.html"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Soccer Team" in activities
    assert "Swimming Club" in activities
    assert "Drama Club" in activities


def test_get_activities_include_required_fields():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    activity = response.json()["Soccer Team"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_succeeds():
    # Arrange
    url = "/activities/Soccer Team/signup"
    params = {"email": "newstudent@mergington.edu"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Signed up" in payload["message"]
    assert "newstudent@mergington.edu" in payload["message"]


def test_signup_for_activity_not_found():
    # Arrange
    url = "/activities/Nonexistent Activity/signup"
    params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(url, params=params)

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_duplicate_student_returns_error():
    # Arrange
    url = "/activities/Drama Club/signup"
    params = {"email": "duplicate@mergington.edu"}

    # Act
    first_response = client.post(url, params=params)
    second_response = client.post(url, params=params)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"]


def test_unregister_from_activity_succeeds():
    # Arrange
    signup_url = "/activities/Art Workshop/signup"
    unregister_url = "/activities/Art Workshop/signup"
    params = {"email": "unregister@mergington.edu"}
    client.post(signup_url, params=params)

    # Act
    response = client.delete(unregister_url, params=params)

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]


def test_unregister_from_activity_not_found():
    # Arrange
    url = "/activities/Nonexistent Activity/signup"
    params = {"email": "student@mergington.edu"}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_student_not_signed_up_returns_error():
    # Arrange
    url = "/activities/Robotics Club/signup"
    params = {"email": "notsignedup@mergington.edu"}

    # Act
    response = client.delete(url, params=params)

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]
