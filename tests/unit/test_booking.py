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

    def test_booking_reflects_updated_count_in_response(self, make_booking, get_competition):
        """
        Checks the in-memory state directly.
        The updated number of places should be reflected
        immediately in the response after booking.
        """
        make_booking('Future Festival', 'Simply Lift', 3)
        competition = get_competition('Future Festival')
        assert competition['numberOfPlaces'] == 22

    # -----------------
    # SAD PATH
    # -----------------

    @pytest.mark.parametrize("competition,club", [
        ("Unknown Competition", "Simply Lift"),
        ("Future Festival", "Unknown Club"),
    ])
    def test_invalid_booking_data_returns_error(self, mock_client, competition, club):
        """
        If either competition or club name is not found,
        the app should return an error message without crashing.
        """
        response = mock_client.post('/purchasePlaces', data={
            'competition': competition,
            'club': club,
            'places': '3'
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


class TestClubPoints:
    """
    Unit tests for club point deduction in purchasePlaces().

    Issue #8: Club point balance is not updated after booking.
    Branch: fix/club-points-not-deducted

    Verifies that points are correctly deducted from the club's
    balance after a successful booking and reflected in the UI.
    """

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_booking_deducts_points_from_club(self, make_booking, get_club):
        """
        After a valid booking, the club's points balance
        should be reduced by the number of places reserved.
        Simply Lift starts with 13 points, books 3 places — expects 10.
        """
        make_booking('Future Festival', 'Simply Lift', 3)
        club = get_club('Simply Lift')
        assert int(club['points']) == 10

    # -----------------
    # SAD PATH
    # -----------------

    @pytest.mark.parametrize("places_requested", [14, 20, 100])
    def test_booking_blocked_when_points_insufficient(
            self, make_booking, places_requested
    ):
        """
        Booking must be rejected whenever requested places
        exceed the club's available points.
        """
        response = make_booking("Future Festival", "Simply Lift", places_requested)

        assert response.status_code == 200
        assert b"insufficient points." in response.data
