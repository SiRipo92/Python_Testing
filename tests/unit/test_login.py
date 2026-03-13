import pytest

class TestLogin:
    """
    Unit tests for the /showSummary route (login).

    Issue #2: Unknown email crashes the app with IndexError 500.
    Branch: fix/login-unknown-email-crash
    """

    # -----------------
    # SAD PATH
    # -----------------
    def test_unknown_email_returns_error_message(self, mock_client):
        """
        An unknown email should return 200 with a clear error
        message instead of crashing with IndexError 500.
        """
        response = mock_client.post(
            '/showSummary',
            data={'email': 'unknown@notfound.com'}
        )
        assert response.status_code == 200
        assert b"Sorry, that email was not found." in response.data

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_valid_email_loads_summary_page(self, mock_client):
        """
        A valid email should load the summary/welcome page
        and display the club's name.
        """
        response = mock_client.post(
            '/showSummary',
            data={'email': 'john@simplylift.co'}
        )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    # -----------------
    # EDGE CASE
    # -----------------

    def test_empty_email_returns_error_message(self, mock_client):
        """
        An empty email submission should return 200 with an
        error message rather than crashing or returning a server error.
        """
        response = mock_client.post(
            '/showSummary',
            data={'email': ''}
        )
        assert response.status_code == 200
        assert b"Sorry, that email was not found." in response.data
