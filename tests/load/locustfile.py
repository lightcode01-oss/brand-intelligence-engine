"""
Nomen — Locust Load Test
Purpose: Distributed load testing with realistic user journeys
Usage: locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
"""

from __future__ import annotations

import json
import random
import string

from locust import HttpUser, TaskSet, between, task


def random_email() -> str:
    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"test_{suffix}@example.com"


class PublicUserTasks(TaskSet):
    """Tasks for unauthenticated public visitors."""

    @task(5)
    def health_check(self) -> None:
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(3)
    def view_plans(self) -> None:
        with self.client.get("/api/v1/billing/plans", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Plans endpoint failed: {response.status_code}")

    @task(2)
    def view_openapi(self) -> None:
        with self.client.get("/api/v1/openapi.json", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"OpenAPI schema failed: {response.status_code}")


class AuthenticatedUserTasks(TaskSet):
    """Tasks for authenticated platform users."""

    token: str = ""

    def on_start(self) -> None:
        """Register and log in before running tasks."""
        email = random_email()
        password = "TestP@ss123!"

        # Register
        reg_response = self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Load Tester"},
        )

        if reg_response.status_code in (200, 201):
            # Login
            login_response = self.client.post(
                "/api/v1/auth/login",
                data={"username": email, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token", "")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(5)
    def view_dashboard(self) -> None:
        if not self.token:
            return
        with self.client.get("/api/v1/workspaces/", catch_response=True) as response:
            if response.status_code in (200, 401):
                response.success()
            else:
                response.failure(f"Workspaces failed: {response.status_code}")

    @task(2)
    def view_analytics(self) -> None:
        if not self.token:
            return
        with self.client.get("/api/v1/analytics/overview", catch_response=True) as response:
            if response.status_code in (200, 401):
                response.success()
            else:
                response.failure(f"Analytics failed: {response.status_code}")

    @task(1)
    def view_profile(self) -> None:
        if not self.token:
            return
        with self.client.get("/api/v1/users/me", catch_response=True) as response:
            if response.status_code in (200, 401):
                response.success()
            else:
                response.failure(f"Profile failed: {response.status_code}")


class PublicUser(HttpUser):
    """Simulates an unauthenticated visitor browsing the platform."""

    tasks = [PublicUserTasks]
    wait_time = between(2, 5)
    weight = 3


class AuthenticatedUser(HttpUser):
    """Simulates a logged-in user actively using the platform."""

    tasks = [AuthenticatedUserTasks]
    wait_time = between(3, 8)
    weight = 1
