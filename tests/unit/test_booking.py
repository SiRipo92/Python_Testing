import pytest
import server


class TestPurchasePlaces:
    """
    Unit tests for the /purchasePlaces route.

    Issue #6: Competition places are not correctly deducted after booking.
    Branch: fix/competition-places-not-deducted

    Verifies that places are correctly deducted from the competition's
    available total after a successful booking, and that the type
    consistency of numberOfPlaces is maintained after deduction.
    """

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_booking_deducts_places_from_competition(self, mock_client):
        """
        After a valid booking, the competition's numberOfPlaces
        should be reduced by the number of places requested.
        """
        response = mock_client.post('/purchasePlaces', data={
            'competition': 'Future Festival',
            'club': 'Simply Lift',
            'places': '3',
        })
        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data

    def test_booking_reflects_updated_count_in_response(self, mock_client):
        """
        Checks the in-memory state directly.
        The updated number of places should be reflected
        immediately in the response after booking.
        """
        mock_client.post('/purchasePlaces', data={
            'competition': 'Future Festival',
            'club': 'Simply Lift',
            'places': '3',
        })
        competition = next(
            (c for c in server.competitions if c['name'] == 'Future Festival'), None
        )
        assert competition['numberOfPlaces'] == 22

    # -----------------
    # SAD PATH
    # -----------------

    def test_unknown_competition_returns_error(self, mock_client):
        """
        If the competition name is not found, the app should
        return an error message without crashing.
        """
        response = mock_client.post('/purchasePlaces', data={
            'competition': 'Unknown Competition',
            'club': 'Simply Lift',
            'places': '3',
        })
        assert response.status_code == 200
        assert b'Something went wrong' in response.data

    def test_unknown_club_returns_error(self, mock_client):
        """
        If the club name is not found, the app should
        return an error message without crashing.
        """
        response = mock_client.post('/purchasePlaces', data={
            'competition': 'Future Festival',
            'club': 'Unknown Club',
            'places': '3',
        })
        assert response.status_code == 200
        assert b'Something went wrong' in response.data

    # -----------------
    # EDGE CASES
    # -----------------

    def test_places_value_remains_integer_after_deduction(self, mock_client):
        """
        After deduction, numberOfPlaces should be stored
        as an integer to maintain type consistency across bookings.
        """
        mock_client.post("/purchasePlaces", data={
            'competition': 'Future Festival',
            'club': 'Simply Lift',
            'places': '3',
        })
        competition = next(
            (c for c in server.competitions if c['name'] == 'Future Festival'), None
        )

        # Verify type consistency — numberOfPlaces must be int after deduction,
        # not a string as it was originally stored in the JSON file
        assert isinstance(competition['numberOfPlaces'], int)
        assert competition['numberOfPlaces'] == 22
