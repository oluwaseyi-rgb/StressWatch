"""
Locust stress watching script — authorized internal testing only.

Install:
    pip install locust --break-system-packages

Run with web UI (recommended — lets you control ramp-up live):
    locust -f stresswatch.py --host https://your-internal-service.company.com

Then open http://localhost:8089 and set:
    - Number of users (peak concurrent users to simulate)
    - Ramp up (users spawned per second)
    - Run time (optional, e.g. 5m)

Run headless (no UI, good for CI):
    locust -f stresswatch.py --host https://your-internal-service.company.com \
        --users 50 --spawn-rate 5 --run-time 5m --headless \
        --html report.html --csv results
"""

import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner


class SiteUser(HttpUser):
    # Simulates real users pausing between actions instead of hammering nonstop
    wait_time = between(1, 3)

    def on_start(self):
        """Runs once per simulated user at the start — good place for login."""
        # Example: authenticate and store a token/session
        # response = self.client.post("/api/login", json={
        #     "username": "testuser",
        #     "password": "testpass"
        # })
        # self.token = response.json().get("token")
        pass

    @task(5)  # weight: this task runs 5x more often than weight-1 tasks
    def view_homepage(self):
        self.client.get("/", name="Homepage")

    @task(3)
    def view_product(self):
        product_id = random.randint(1, 1000)
        # `name=` groups all these under one stat line instead of one per ID
        self.client.get(f"/api/products/{product_id}", name="/api/products/[id]")

    @task(2)
    def search(self):
        terms = ["laptop", "phone", "headphones", "monitor"]
        self.client.get(
            "/api/search",
            params={"q": random.choice(terms)},
            name="/api/search"
        )

    @task(1)
    def submit_form(self):
        with self.client.post(
            "/api/contact",
            json={"name": "Load Test", "message": "test payload"},
            name="/api/contact",
            catch_response=True
        ) as response:
            # Custom pass/fail logic beyond just HTTP status code
            if response.status_code == 200 and "success" in response.text:
                response.success()
            else:
                response.failure(f"Unexpected response: {response.status_code}")


# --- Event hooks: useful for custom logging/alerting during the test ---

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    if exception:
        print(f"Request failed: {name} -> {exception}")
    elif response_time > 2000:  # flag anything slower than 2s
        print(f"Slow request: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Load test starting — monitor server-side CPU/memory/error rates now.")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test complete. Check report.html / results_*.csv for details.")
