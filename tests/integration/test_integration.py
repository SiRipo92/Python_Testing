import pytest
import server


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

        # Step 1 — check points board BEFORE booking
        response = mock_client.get('/pointsBoard')
        assert response.status_code == 200
        assert b'Simply Lift' in response.data
        assert b'13' in response.data
        points_before = 13
        print(f"\n→ Points before booking: {points_before}")

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

        # Step 4 — purchase 3 places
        places_booked = 3
        response = make_booking('Future Festival', 'Simply Lift', places_booked)
        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data

        # Check changes in points
        expected_points = points_before - places_booked  # 13 - 3 = 10
        assert f'{expected_points}'.encode() in response.data
        print(f"→ Expected points after: {expected_points}")

        # Check competition places reduced in response
        assert b'22' in response.data  # 25 - 3 = 22

        # Step 5 — logout
        response = mock_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

        # Step 6 — check points board AFTER booking
        # Points board must reflect the same deduction seen in step 4
        response = mock_client.get('/pointsBoard')
        assert b'Simply Lift' in response.data
        assert f'{expected_points}'.encode() in response.data
        assert b'13' not in response.data  # old value must be gone
        print(f"→ Points board response contains '10': {b'10' in response.data}")
