from copy import deepcopy
import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(activities)
        self.client = TestClient(app)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)
        self.client.close()

    def test_unregister_removes_only_selected_participant(self):
        response = self.client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Unregistered michael@mergington.edu from Chess Club"},
        )
        remaining = self.client.get("/activities").json()
        self.assertEqual(
            remaining["Chess Club"]["participants"], ["daniel@mergington.edu"]
        )
        self.assertEqual(
            remaining["Gym Class"], self.original_activities["Gym Class"]
        )

    def test_unknown_activity(self):
        response = self.client.delete(
            "/activities/Unknown/signup", params={"email": "student@example.com"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Activity not found")
        self.assertEqual(activities, self.original_activities)

    def test_unknown_participant(self):
        response = self.client.delete(
            "/activities/Chess%20Club/signup", params={"email": "unknown@example.com"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Student is not signed up")
        self.assertEqual(activities, self.original_activities)

    def test_signup_unregister_and_signup_again(self):
        params = {"email": "student+club@example.com"}
        url = "/activities/Art%20Club/signup"
        self.assertEqual(self.client.post(url, params=params).status_code, 200)
        self.assertEqual(self.client.delete(url, params=params).status_code, 200)
        self.assertEqual(activities["Art Club"]["participants"], [])
        self.assertEqual(self.client.delete(url, params=params).status_code, 404)
        self.assertEqual(self.client.post(url, params=params).status_code, 200)

    def test_email_required(self):
        response = self.client.delete("/activities/Chess%20Club/signup")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(activities, self.original_activities)
