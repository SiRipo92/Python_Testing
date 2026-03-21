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

    @pytest.mark.parametrize("email", [
        "unknown@notfound.com",
        "",
        "notanemail",
    ])
    def test_invalid_email_returns_error_message(self, mock_client, email):
        """
        Any email that does not match a club in the database
        should return 200 with a graceful error message — not crash.
        Covers unknown, empty, and malformed email inputs.
        """
        response = mock_client.post(
            '/showSummary',
            data={'email': email}
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
