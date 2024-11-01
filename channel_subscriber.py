from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import logging


class ChannelSubscriber:
    def __init__(self):
        self.driver = None
        self.BUTTON_WAIT_TIME = 10
        self.DELAY_BETWEEN_CHANNELS = 1

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            filename="youtube_subscription.log",
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

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
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "ytd-masthead"))
                )

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

    def wait_for_button(self):
        """Wait for the subscribe button to be present on the page."""
        try:
            # Wait for any subscribe button (subscribed or not)
            subscribe_button = WebDriverWait(self.driver, self.BUTTON_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ytd-subscribe-button-renderer")
                )
            )

            # Ensure the button is visible
            WebDriverWait(self.driver, 5).until(EC.visibility_of(subscribe_button))
            time.sleep(2)  # Small delay to allow animation to load
            return True
        except TimeoutException:
            print("Button not found in time.")
            return False

    def subscribe(self, channel_name):
        """Attempt to subscribe to a YouTube channel."""
        try:
            # First find the button container
            button_container = WebDriverWait(self.driver, self.BUTTON_WAIT_TIME).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ytd-subscribe-button-renderer")
                )
            )

            # Find the button text element
            button_text = (
                button_container.find_element(
                    By.CSS_SELECTOR, "yt-formatted-string.ytd-subscribe-button-renderer"
                )
                .text.strip()
                .lower()
            )

            print(f"Found button text: '{button_text}'")

            if button_text == "subscribe":
                print(f"Subscribing to {channel_name}")
                subscribe_button = button_container.find_element(
                    By.CSS_SELECTOR, "button.yt-spec-button-shape-next"
                )
                self.driver.execute_script("arguments[0].click();", subscribe_button)
                print(f"Subscribed successfully to {channel_name}")
                return 1
            elif button_text == "subscribed":
                print(f"Already subscribed to {channel_name}")
                return 0
            else:
                print(f"Unexpected button text: '{button_text}'")
                return -1

        except Exception as e:
            logging.exception(f"An error occurred while subscribing to {channel_name}")
            print(f"Failed to subscribe to {channel_name}: {str(e)}")
            return -1

    def ensure_english_language(self):
        """Check and change YouTube language to English if needed."""
        try:
            # Click avatar button to open menu
            avatar_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#avatar-btn"))
            )
            avatar_btn.click()
            # time.sleep(1)

            # Try multiple selectors for the language menu item
            selectors = [
                # Try by SVG path
                "//ytd-compact-link-renderer[.//path[@d='M13.33 6c-1 2.42-2.22 4.65-3.57 6.52l2.98 2.94-.7.71-2.88-2.84c-.53.67-1.06 1.28-1.61 1.83l-3.19 3.19-.71-.71 3.19-3.19c.55-.55 1.08-1.16 1.6-1.83l-.16-.15c-1.11-1.09-1.97-2.44-2.49-3.9l.94-.34c.47 1.32 1.25 2.54 2.25 3.53l.05.05c1.2-1.68 2.29-3.66 3.2-5.81H2V5h6V3h1v2h7v1h-2.67zM22 21h-1l-1.49-4h-5.02L13 21h-1l4-11h2l4 11zm-2.86-5-1.86-5h-.56l-1.86 5h4.28z']]",
                # Try by text content
                "//ytd-compact-link-renderer[.//yt-formatted-string[contains(text(), 'Language') or contains(text(), 'Sprache')]]",
                # Try by icon class
                "//ytd-compact-link-renderer[.//yt-icon[contains(@class, 'language-icon')]]",
            ]

            language_item = None
            for selector in selectors:
                try:
                    language_item = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue

            if not language_item:
                print("Could not find language selector")
                return False

            language_item.click()
            # time.sleep(1)

            # Find and click the English option
            english_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//ytd-compact-link-renderer[.//yt-formatted-string[contains(text(), 'English') and contains(text(), '(US)')]]",
                    )
                )
            )
            english_option.click()
            # time.sleep(2)

            # Refresh and wait
            self.driver.refresh()
            # time.sleep(2)
            print("Language changed to English")
            return True

        except Exception as e:
            print(f"Error changing language: {str(e)}")
            logging.exception("Language change failed")
            return False

    def subscribe_to_channels(self, channels):
        """Main method to perform subscriptions"""
        try:
            self.driver = self.get_secure_driver()
            self.driver.get("https://www.youtube.com")

            if not self.wait_for_login():
                return 0, 0, 0

            self.ensure_english_language()

            active_channels = [channel for channel in channels if channel[2]]
            total_active = len(active_channels)

            print("\n" + "=" * 58)
            print("Ready to start subscribing:")
            print(f"✓ Logged in successfully")
            print(f"✓ Language set to English")
            print(f"✓ Found {total_active} channels to process")
            print("=" * 58)

            input("\nPress Enter to start subscribing to channels...")
            print("\nStarting subscription process...")

            total_processed = 0
            already_subscribed = 0
            new_subscriptions = 0

            for i, (name, url, _) in enumerate(active_channels, 1):
                print(
                    f"\nChecking {name} ({i}/{total_active}, {i/total_active*100:.1f}% done)"
                )
                self.driver.get(url)

                if self.wait_for_button():
                    result = self.subscribe(name)
                    if result == 1:
                        new_subscriptions += 1
                    elif result == 0:
                        already_subscribed += 1
                    total_processed += 1
                else:
                    print(f"Subscribe button not found for {name}")

                time.sleep(self.DELAY_BETWEEN_CHANNELS)

            return total_processed, already_subscribed, new_subscriptions
        finally:
            if self.driver:
                self.driver.quit()
