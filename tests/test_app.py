"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "maria@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays, musicals, and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Digital Art Studio": {
            "description": "Create digital artwork, animations, and graphic design projects",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["clara@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for fetching activities"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_include_participants(self, reset_activities):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Chess Club"]
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_activities_include_details(self, reset_activities):
        """Test that activities include all required details"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_new_participant(self, reset_activities):
        """Test signing up a new participant for an activity"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "signed up" in data["message"].lower()
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, reset_activities):
        """Test that signing up duplicate participant fails"""
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, reset_activities):
        """Test that signing up for nonexistent activity fails"""
        response = client.post("/activities/Fake%20Activity/signup?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_participant(self, reset_activities):
        """Test unregistering a participant from an activity"""
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "unregistered" in data["message"].lower()
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, reset_activities):
        """Test that unregistering a non-registered participant fails"""
        response = client.delete("/activities/Chess%20Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test that unregistering from nonexistent activity fails"""
        response = client.delete("/activities/Fake%20Activity/unregister?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")
