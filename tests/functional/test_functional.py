import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import server


BASE_URL = 'http://localhost:5001'

@pytest.fixture(scope="session")
def app_server():
    """
    Starts the Flask server in a background thread for Selenium tests.
    Session-scoped — starts once, shared across all functional tests.
    """
    thread = threading.Thread(target=lambda: server.app.run(
        port=5001,
        debug=False,
        use_reloader=False
    ))
    thread.daemon = True
    thread.start()
    time.sleep(1)  # Give server time to start
    yield
    # Thread stops automatically when session ends


@pytest.fixture(scope="session")
def driver():
    """
    Provides a headless Chrome browser for Selenium tests.
    Session-scoped — browser opens once, shared across all functional tests.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chrome_driver = webdriver.Chrome(options=options)
    yield chrome_driver
    chrome_driver.quit()


class TestFunctionalUserJourney:
    """
    Functional tests using Selenium WebDriver.
    Tests real browser interactions against a running Flask server.

    Requires:
    - Flask server running in background thread (app_server fixture)
    - Headless Chrome browser (driver fixture)
    """

    def login(self, driver, email="john@simplylift.co"):
        """
        Helper method — navigates to index and logs in with given email.
        Reusable across any test that requires authentication.
        """
        driver.get(BASE_URL + "/")
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys(email)
        email_input.submit()
        time.sleep(1)

    # -----------------
    # HAPPY PATH
    # -----------------

    def test_index_page_loads(self, app_server, driver):
        """
        Homepage loads and displays the login form.
        Verifies the server is running and the index route works.
        """
        driver.get(BASE_URL + "/")
        assert "GUDLFT" in driver.title or "Registration" in driver.title
        email_input = driver.find_element(By.NAME, "email")
        assert email_input is not None

    def test_valid_login_loads_summary(self, app_server, driver):
        """
        Valid email submission redirects to welcome page
        showing club name and available points.
        """
        self.login(driver)
        assert "Welcome" in driver.page_source
        assert "john@simplylift.co" in driver.page_source

    def test_booking_flow(self, app_server, driver):
        """
        Login -> click 'Book Places' -> Submit booking -> confirmation message
        """
        self.login(driver)
        # click Book Places for first available competition
        book_link = driver.find_element(By.LINK_TEXT, "Book Places")
        book_link.click()
        time.sleep(1)
        # fill in form with number of places to book
        places_input = driver.find_element(By.NAME, "places")
        places_input.clear()
        places_input.send_keys("2")
        places_input.submit()
        time.sleep(1)
        assert "Great-booking complete!" in driver.page_source

    def test_points_board_loads_without_login(self, app_server, driver):
        """
        Points board is publicly accessible without login.
        Shows club names and points
        """
        driver.get(BASE_URL + "/pointsBoard")
        assert "Simply Lift" in driver.page_source
