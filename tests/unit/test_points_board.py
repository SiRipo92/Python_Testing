import pytest
import server


class TestPointsBoard():
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
