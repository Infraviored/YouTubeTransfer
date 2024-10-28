from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import os
from selenium.webdriver.chrome.options import Options


class ChannelExtractor:
    def __init__(self):
        self.driver = None

    def get_secure_driver(self):
        """Create a new Chrome driver with all security bypasses."""
        options = Options()
        # Basic options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Security bypass options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--disable-gpu")

        # Window options
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")

        # User agent and automation flags
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)

        # Additional stealth settings
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            },
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return self.driver

    def wait_for_login(self):
        """Wait for the user to log in to YouTube."""
        print("Please log in to your YouTube account in the opened browser window.")
        print("Note: You only need to log in for this session, not to Chrome itself.")

        max_retries = 5
        retries = 0

        while retries < max_retries:
            try:
                # Wait for page load with longer timeout
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "ytd-masthead"))
                )

                # Check for avatar button
                try:
                    avatar = WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "button#avatar-btn")
                        )
                    )
                    if avatar.is_displayed():
                        print("Login detected via avatar. Proceeding...")
                        return True
                except TimeoutException:
                    retries += 1
                    choice = input(
                        f"\nLogin not detected (attempt {retries}/{max_retries}). Enter 'r' to retry or 'q' to quit: "
                    )
                    if choice.lower() == "q":
                        return False
                    self.driver.refresh()
                    time.sleep(2)
                    continue

            except Exception as e:
                print(f"Error checking login status: {str(e)}")
                retries += 1
                time.sleep(2)

        print("Maximum retry attempts reached. Please try again later.")
        return False

    def wait_for_channels_page(self):
        """Wait for the channels page to fully load."""
        try:
            # Wait for channel elements to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-channel-renderer"))
            )
            # Wait a bit more for dynamic content
            time.sleep(2)
            return True
        except TimeoutException:
            print("Could not detect channel elements on the page.")
            return False

    def save_channels_page(self):
        """Save the channels page HTML to a file."""
        try:
            # Get the page source after waiting for content
            html_content = self.driver.page_source

            # Save to Downloads folder
            downloads_dir = os.path.expanduser("~/Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            file_path = os.path.join(downloads_dir, "YouTube.html")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"Successfully saved channels page to: {file_path}")
            return file_path
        except Exception as e:
            print(f"Error saving channels page: {str(e)}")
            return None

    def extract_channels(self, file_path):
        """Extract channel information from a saved HTML file."""
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        soup = BeautifulSoup(content, "html.parser")
        channel_renderers = soup.find_all("ytd-channel-renderer")

        channels = []
        for renderer in channel_renderers:
            link = renderer.find("a", class_="channel-link")
            if link:
                channel_url = link["href"]
                channel_name = channel_url.split("@")[-1]
                if channel_url.startswith("/"):
                    channel_url = "https://www.youtube.com" + channel_url
                channels.append((channel_name, channel_url, True))

        return channels

    def get_channel_list(self):
        """Main method to get channel list"""
        try:
            self.driver = self.get_secure_driver()

            # Login phase
            self.driver.get("https://www.youtube.com")
            if not self.wait_for_login():
                return None

            # Get channels page
            print("\nNavigating to channels page...")
            self.driver.get("https://www.youtube.com/feed/channels")

            if self.wait_for_channels_page():
                file_path = self.save_channels_page()
                if file_path and os.path.exists(file_path):
                    channels = self.extract_channels(file_path)
                    return channels

            return None
        finally:
            if self.driver:
                self.driver.quit()
