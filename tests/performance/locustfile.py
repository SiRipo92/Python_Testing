from locust import HttpUser, task, between
import threading
import time
import server

# --- Factory functions to generate large datasets ---

def generate_clubs(n=500):
    """
    Generates n fake clubs for load testing.
    Simulates a large dataset to stress test /pointsBoard
    and /showSummary routes.
    """
    return [
        {
            "name": f"Club {i}",
            "email": f"club{i}@test.com",
            "points": "50"
         }
        for i in range(n)
    ]


def generate_competitions(n=100):
    """
    Generates n fake competitions for load testing.
    Simulates a large dataset to stress test /showSummary route.
    """
    return [
        {
            "name": f"Competition {i}",
            "date": "2030-01-01 10:00:00",
            "numberOfPlaces": "25"
        }
        for i in range(n)
    ]


# --- Inject large datasets into server before tests ---
server.clubs = generate_clubs(500)
server.competitions = generate_competitions(100)


# Start Flask with factory data in background thread
thread = threading.Thread(
    target=lambda: server.app.run(port=5002, debug=False, use_reloader=False)
)
thread.daemon = True
thread.start()
time.sleep(1)

class GudlftUser(HttpUser):
    """
    Simulates a GUDLFT user performing typical actions.
    wait_time: simulated user waits 1-3 seconds between requests.
    """
    wait_time = between(1, 3)

    @task(2)
    def view_points_board(self):
        """
        Performance requirement: /pointsBoard must load in under 5 seconds.
        Higher weight (2) — this is the primary page under test.
        """
        with self.client.get("/pointsBoard", catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(
                    f"Points board too slow: {response.elapsed.total_seconds():.2f}s"
                )
            elif response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}")
            else:
                response.success()

    @task(1)
    def view_summary(self):
        """
        Performance requirement: /showSummary must load in under 5 seconds.
        Simulates a logged-in user viewing the competition list.
        """
        with self.client.post(
            "/showSummary",
            data={"email": "club1@test.com"},
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(
                    f"Summary too slow: {response.elapsed.total_seconds():.2f}s"
                )
            elif response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}")
            else:
                response.success()

    @task(1)
    def purchase_places(self):
        """
        Performance requirement: /purchasePlaces must respond in under 2 seconds.
        Simulates a booking — this is the route that updates club points.
        """
        with self.client.post(
                "/purchasePlaces",
                data={
                    "competition": "Competition 0",
                    "club": "Club 1",
                    "places": "1"
                },
                catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure(
                    f"Purchase too slow: {response.elapsed.total_seconds():.2f}s"
                )
            elif response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}")
            else:
                response.success()
