import server


class TestPointsBoard:
    """
    Unit tests for the /points-board route.

    Issue #9: Implement public points display board.
    Branch: feature/points-board

    Verifies that:
    - Page loads with 200 for any user (no login required)
    - Club names and points are displayed
    - Club emails are NOT displayed (privacy)
    """

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_points_board_returns_200(self, mock_client):
        """
        Points board should be publicly accessible.
        No login required - GET request with no session data.
        """
        response = mock_client.get('/pointsBoard')
        assert response.status_code == 200

    def test_points_board_displays_club_names_and_points(self, mock_client):
        """
        Points board must show each club's name and points balance.
        """
        response = mock_client.get('/pointsBoard')
        assert b"Simply Lift" in response.data
        assert b"13" in response.data

    def test_points_board_does_not_display_emails(self, mock_client):
        """
        Verifies that the email data inside clubs is not exposed in table
        """
        response = mock_client.get('/pointsBoard')
        assert b"john@simplylift.co" not in response.data

    # -----------------
    # SAD PATH
    # -----------------

    def test_points_board_displays_message_when_no_clubs(self, mock_client, monkeypatch):
        """
        Edge case: If clubs list is empty, page should still load
        without crashing and show an appropriate message.
        """
        monkeypatch.setattr(server, 'clubs', [])
        response = mock_client.get('/pointsBoard')
        assert response.status_code == 200
        assert b"No clubs registered." in response.data
