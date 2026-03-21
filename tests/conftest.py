import pytest
import server
from server import app


# --- Mock data fixtures ---

@pytest.fixture
def mock_clubs():
    """
    Returns a controlled list of mock clubs for testing.
    Includes real-world clubs plus edge cases (zero points, one point)
    to cover boundary conditions without touching clubs.json.
    """
    return [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"},
        # Edge cases
        {"name": "Zero Points Club", "email": "zero@club.com", "points": "0"},
        {"name": "One Point Club", "email": "one@club.com", "points": "1"},
    ]

@pytest.fixture
def mock_competitions():
    """
    Returns a controlled list of mock competitions for testing.
    Includes future competitions, edge cases (full, almost full),
    and past competitions to cover all validation scenarios
    without touching competitions.json.
    """
    return [
        # Future competitions — valid for booking
        {
            "name": "Future Festival",
            "date": "2030-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Future Classic",
            "date": "2030-10-22 13:30:00",
            "numberOfPlaces": "13"
        },
        # Edge cases for place availability
        {
            "name": "Almost Full Competition",
            "date": "2030-06-15 10:00:00",
            "numberOfPlaces": "1"
        },
        {
            "name": "Full Competition",
            "date": "2030-07-20 10:00:00",
            "numberOfPlaces": "0"
        },
        # Past competitions — visible but not bookable
        {
            "name": "Past Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Past Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        },
    ]


# --- App fixtures ---

@pytest.fixture
def get_club():
    """
    Returns a callable to look up a club from server state by name.
    Avoids repeating next() lookups across test files.
    """
    def _get_club(name):
        return next(
            (c for c in server.clubs if c['name'] == name), None
        )
    return _get_club


@pytest.fixture
def get_competition():
    """
    Returns a callable to look up a competition from server state by name.
    Avoids repeating next() lookups across test files.
    """
    def _get_competition(name):
        return next(
            (c for c in server.competitions if c['name'] == name), None
        )
    return _get_competition

@pytest.fixture
def client():
    """
    Provides a basic Flask test client with TESTING mode enabled.
    Uses the real clubs.json and competitions.json data.
    Only use this fixture for tests that specifically need real data.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_client(client, mock_clubs, mock_competitions, monkeypatch):
    """
    Flask test client with fully isolated mock data injected via monkeypatch.
    Use this in all unit and integration tests to ensure test isolation.
    """
    monkeypatch.setattr(server, 'clubs', mock_clubs)
    monkeypatch.setattr(server, 'competitions', mock_competitions)
    yield client

@pytest.fixture
def make_booking(mock_client):
    """
    Helper fixture that returns a callable for submitting booking requests.

    Depends on mock_client — mock data is automatically injected, meaning
    tests using this fixture never touch clubs.json or competitions.json.

    Usage:
        def test_something(self, make_booking):
            response = make_booking('Future Festival', 'Simply Lift', 3)
            assert response.status_code == 200

    Args:
        competition (str): Name of the competition to book
        club (str): Name of the club making the booking
        places (int): Number of places to request

    Returns:
        Flask test response object
    """

    def _make_booking(competition, club, places):
        return mock_client.post(
            "/purchasePlaces",
            data={
                "competition": competition,
                "club": club,
                "places": str(places),
            },
        )

    return _make_booking
