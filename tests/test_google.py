import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def _chrome_driver() -> webdriver.Chrome:
    """Return a Chrome WebDriver configured for both local and CI environments."""
    options = Options()
    options.add_argument("--headless=new")       # headless mode (required on CI)
    options.add_argument("--no-sandbox")          # required inside containers / root user
    options.add_argument("--disable-dev-shm-usage")  # avoid /dev/shm size limits on Linux
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


# Optional: link to an existing ADO Test Case ID so results update that item.
# Remove the decorator to let the publisher auto-create the Test Case by title.
# @pytest.mark.testcase(1001)
def test_google_title():
    driver = _chrome_driver()
    try:
        driver.get("https://www.google.com")
        assert "Google" in driver.title
    finally:
        driver.quit()
