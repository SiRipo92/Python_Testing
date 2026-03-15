import pytest
import server
import logging

logger = logging.getLogger(__name__)


# --- Fixture needed for integration tests  ---
# Needed to ensure server.clubs and server.competitions are reset
# to mock data before each test, not just after.

@pytest.fixture(autouse=True)
def reset_server_data(monkeypatch, mock_clubs, mock_competitions):
    monkeypatch.setattr(server, 'clubs', mock_clubs)
    monkeypatch.setattr(server, 'competitions', mock_competitions)

class TestUserJourney:
    """
    Integration tests for the core user journey.
    Tests multiple routes working together in sequence.
    """

    def test_full_booking_journey(self, mock_client, make_booking):
        """
        Flow: Points Board → Login → Book → Purchase → Logout → Points Board

        Verifies that state is consistent across all routes:
        - Points deducted from club after booking
        - Places deducted from competition after booking
        - Points board reflects updated balance after logout
        """

        CLUB = 'Simply Lift'
        COMPETITION = 'Future Festival'
        PLACES_TO_BOOK = 3
        POINTS_START = 13
        PLACES_START = 25

        logger.info("=" * 40)
        logger.info("TESTING: full user journey with point and reservation deductions")
        logger.info(f"START: {CLUB} points={POINTS_START}, {COMPETITION} places={PLACES_START}")

        # Step 1 — points board BEFORE booking
        response = mock_client.get('/pointsBoard')
        assert response.status_code == 200
        assert b'Simply Lift' in response.data
        assert b'13' in response.data

        # Step 2 — login
        response = mock_client.post('/showSummary', data={
            'email': 'john@simplylift.co'
        })
        assert response.status_code == 200
        assert b'Welcome, john@simplylift.co' in response.data

        # Step 3 — access booking page
        response = mock_client.get('/book/Future%20Festival/Simply%20Lift')
        assert response.status_code == 200
        assert b'Future Festival' in response.data

        # Step 4 — purchase places
        response = make_booking(COMPETITION, CLUB, PLACES_TO_BOOK)
        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data

        expected_points = POINTS_START - PLACES_TO_BOOK  # 13 - 3 = 10
        expected_places = PLACES_START - PLACES_TO_BOOK  # 25 - 3 = 22

        assert f'{expected_points}'.encode() in response.data
        assert f'{expected_places}'.encode() in response.data
        logger.info(f"AFTER PURCHASE: {CLUB} points={expected_points}, {COMPETITION} places={expected_places}")

        # Step 5 — logout
        response = mock_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

        # Step 6 — points board AFTER booking
        response = mock_client.get('/pointsBoard')
        assert b'Simply Lift' in response.data
        assert f'{expected_points}'.encode() in response.data
        assert b'13' not in response.data
        logger.info(f"POINTS BOARD CONFIRMS: {CLUB} = {expected_points} points ✓")
        logger.info("=" * 40)
