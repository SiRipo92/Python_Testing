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

    def test_index_page_loads(self, app_server, driver):
        """
        Homepage loads and displays the login form.
        Verifies the server is running and the index route works.
        """
        driver.get(BASE_URL+"/")
        assert "GUDLFT" in driver.title or "Registration" in driver.title
        email_input = driver.find_element(By.NAME, "email")
        assert email_input is not None
