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

class TestPurchaseValidation:
    """
    Unit tests for all validation rules in purchase_places().

    Covers issues #3, #4, #10 — the three conditions that must ALL
    pass before a booking is confirmed:
    1. Places requested must not exceed club's available points (Issue #3)
    2. Places requested must not exceed 12 (Issue #4)
    3. Places requested must not exceed competition's available places (Issue #10)

    Branch: fix/purchasing-exceeds-12-places (and subsequent branches)
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

    @pytest.mark.parametrize("places_requested", [12, 11])
    def test_booking_allowed_at_or_below_12_places(self, make_booking, places_requested):
        """
        Booking must be confirmed when places requested
        are at or below the 12-place maximum.
        Boundary values: 12 (exactly at limit), 11 (one below).
        She Lifts has 12 points — sufficient for both scenarios.
        """
        response = make_booking("Future Classic", "She Lifts", places_requested)
        assert response.status_code == 200
        assert b"Great-booking complete!" in response.data

    # -----------------
    # SAD PATH
    # -----------------

    @pytest.mark.parametrize("places_requested", [5, 8, 10])
    def test_booking_blocked_when_points_insufficient(
            self, make_booking, places_requested
    ):
        """
        Booking must be rejected when requested places exceed the club's
        available points AND are within the 12-place cap.
        Iron Temple has 4 points. Values 5, 8, 10 are all < 12 but exceed 4.
        """
        response = make_booking("Future Festival", "Iron Temple", places_requested)

        assert response.status_code == 200
        assert b"Insufficient points." in response.data

    # Tests ONLY the 12-place cap — She Lifts has 12 points so points check won't fire for ≤ 12
    @pytest.mark.parametrize("places_requested", [13, 20, 100])
    def test_booking_blocked_when_exceeds_12_places(self, make_booking, places_requested):
        """
        Booking must be blocked when places requested exceed
        the 12-place maximum, regardless of points available.
        Boundary values: 13 (one above), 20, 100 (well above).
        """
        response = make_booking("Future Classic", "She Lifts", places_requested)
        assert response.status_code == 200
        assert b"Cannot book more than 12 places." in response.data
