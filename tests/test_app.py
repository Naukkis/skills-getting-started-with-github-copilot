"""
Tests for the Mergington High School FastAPI application
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_root_redirect():
    """Test that GET / redirects to the static index page"""
    response = client.get("/")
    # TestClient follows redirects by default
    assert response.status_code == 200
    # The response should contain HTML content from index.html
    assert "<!DOCTYPE html>" in response.text
    assert "Mergington High School" in response.text


def test_get_activities():
    """Test GET /activities returns all activities with correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities
    
    # Check that some expected activities are present
    expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]
    for activity in expected_activities:
        assert activity in data
    
    # Verify structure of first activity
    first_activity = next(iter(data.values()))
    required_fields = ["description", "schedule", "max_participants", "participants"]
    for field in required_fields:
        assert field in first_activity
    
    assert isinstance(first_activity["participants"], list)
    assert isinstance(first_activity["max_participants"], int)


def test_signup_success():
    """Test successful signup for an activity"""
    test_email = "test_signup@example.com"
    activity_name = "Chess Club"
    
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "Signed up" in result["message"]
    assert test_email in result["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert test_email in data[activity_name]["participants"]


def test_signup_duplicate():
    """Test that duplicate signup returns 400 error"""
    test_email = "test_duplicate@example.com"
    activity_name = "Programming Class"
    
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Second signup with same email
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 400
    
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity():
    """Test signup for non-existent activity returns 404"""
    test_email = "test_nonexistent@example.com"
    activity_name = "Nonexistent Activity"
    
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_delete_participant_success():
    """Test successful deletion of a participant"""
    test_email = "test_delete@example.com"
    activity_name = "Gym Class"
    
    # First add the participant
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Now delete them
    response = client.delete(f"/activities/{activity_name}/participants/{test_email}")
    assert response.status_code == 200
    
    result = response.json()
    assert "message" in result
    assert "Removed" in result["message"]
    assert test_email in result["message"]
    
    # Verify they were removed
    response = client.get("/activities")
    data = response.json()
    assert test_email not in data[activity_name]["participants"]


def test_delete_nonexistent_participant():
    """Test deleting non-existent participant returns 404"""
    test_email = "nonexistent_participant@example.com"
    activity_name = "Basketball Team"
    
    response = client.delete(f"/activities/{activity_name}/participants/{test_email}")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "Participant not found" in result["detail"]


def test_delete_nonexistent_activity():
    """Test deleting from non-existent activity returns 404"""
    test_email = "test@example.com"
    activity_name = "Nonexistent Activity"
    
    response = client.delete(f"/activities/{activity_name}/participants/{test_email}")
    assert response.status_code == 404
    
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]