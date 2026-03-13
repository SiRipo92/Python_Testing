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
    def test_unknown_email_returns_error_message(self, client_with_mock_data):
        """
        An unknown email should return 200 with a clear error
        message instead of crashing with IndexError 500.
        """
        response = client_with_mock_data.post(
            '/showSummary',
            data={'email': 'unknown@notfound.com'}
        )
        assert response.status_code == 200
        assert b"Sorry, that email wasn't found." in response.data

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_valid_email_loads_summary_page(self, client_with_mock_data):
        """
        A valid email should load the summary/welcome page
        and display the club's name.
        """
        response = client_with_mock_data.post(
            '/showSummary',
            data={'email': 'john@simplylift.co'}
        )
        assert response.status_code == 200
        assert b"Welcome" in response.data
