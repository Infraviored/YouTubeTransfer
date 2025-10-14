import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)  # Add this import


# Configuration
BUTTON_WAIT_TIME = 10  # Seconds to wait for button to appear
PAGE_LOAD_WAIT_TIME = 3  # Seconds to wait after page load before checking for button
DELAY_BETWEEN_CHANNELS = 1  # Seconds to wait between processing channels


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="youtube_subscription.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def wait_for_button(driver):
    """
    Wait for the subscribe button to be present on the page.
    """
    try:
        # Wait for the button element to be present (Subscribe or Subscribed)
        subscribe_button = WebDriverWait(driver, BUTTON_WAIT_TIME).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content')]",
                )
            )
        )

        # Ensure the button is visible
        WebDriverWait(driver, 5).until(EC.visibility_of(subscribe_button))
        return True
    except TimeoutException:
        return False


def subscribe(driver, channel_name):
    """
    Attempt to subscribe to a YouTube channel.
    """
    try:
        # Wait for the button element and ensure it's visible
        subscribe_button = WebDriverWait(driver, BUTTON_WAIT_TIME).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content')]",
                )
            )
        )

        # Ensure the button is visible
        WebDriverWait(driver, 5).until(EC.visibility_of(subscribe_button))

        # Small delay to ensure text is loaded
        time.sleep(2)

        # Get button text, try JavaScript if normal method fails
        button_text = subscribe_button.text.strip().lower()
        if not button_text:
            print("Retrieving button text via JavaScript...")
            button_text = (
                driver.execute_script(
                    "return arguments[0].textContent;", subscribe_button
                )
                .strip()
                .lower()
            )

        print(f"Detected Text '{button_text}'")

        if button_text == "subscribe":
            print(f"Subscribing to {channel_name}")
            driver.execute_script("arguments[0].click();", subscribe_button)
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
        print(f"Failed to subscribe to {channel_name}")
        return -1


def get_secure_driver():
    """
    Create a new Chrome driver with all security bypasses.

    Returns:
    webdriver: Configured Chrome webdriver instance
    """
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

    driver = webdriver.Chrome(options=options)

    # Additional stealth settings
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        },
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def ensure_english_language(driver):
    """
    Check and change YouTube language to English if needed by finding the unique language SVG icon.
    """
    try:
        # Click avatar button to open menu
        avatar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#avatar-btn"))
        )
        avatar_btn.click()
        time.sleep(1)

        # Find and click language menu item by its unique SVG path
        language_svg = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//svg[.//path[starts-with(@d, 'M13.33 6c-1 2.42-2.22 4.65-3.57 6.52')]]",
                )
            )
        )
        # Click the parent tp-yt-paper-item
        language_item = language_svg.find_element(
            By.XPATH, "ancestor::tp-yt-paper-item"
        )
        language_item.click()
        time.sleep(1)

        # Click English (US) option
        english_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//tp-yt-paper-item[.//yt-formatted-string[contains(text(), 'English (US)')]]",
                )
            )
        )
        english_option.click()
        time.sleep(2)

        # Refresh the page
        driver.refresh()
        time.sleep(2)
        print("Language changed to English")
        return True

    except Exception as e:
        print(f"Error changing language: {str(e)}")
        return False


def subscribe_to_channels(channels):
    """
    Subscribe to a list of YouTube channels.

    Args:
    channels (list): List of tuples containing (channel_name, channel_url, active_status)

    Returns:
    tuple: (total_processed, already_subscribed, new_subscriptions)
    """
    driver = get_secure_driver()  # Use secure driver here
    driver.get("https://www.youtube.com")

    if not wait_for_login(driver):
        driver.quit()
        return 0, 0, 0

    ensure_english_language(driver)

    total_processed = 0
    already_subscribed = 0
    new_subscriptions = 0
    active_channels = [channel for channel in channels if channel[2]]
    total_active = len(active_channels)

    for i, (name, url, _) in enumerate(active_channels, 1):
        print("\n" + "-" * 58)
        print(f"Checking {name} ({i}/{total_active}, {i/total_active*100:.1f}% done)")
        driver.get(url)

        if wait_for_button(driver):
            result = subscribe(driver, name)
            if result == 1:
                new_subscriptions += 1
            elif result == 0:
                already_subscribed += 1
            total_processed += 1
        else:
            print(f"Subscribe button not found for {name}")

        time.sleep(DELAY_BETWEEN_CHANNELS)

    driver.quit()
    return total_processed, already_subscribed, new_subscriptions


def extract_channels(file_path):
    """
    Extract channel information from a saved HTML file.

    Args:
    file_path (str): Path to the saved HTML file

    Returns:
    list: List of tuples containing (channel_name, channel_url, active_status)
    """
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


def display_channels(channels):
    """
    Display the list of channels in a formatted manner.

    Args:
    channels (list): List of tuples containing (channel_name, channel_url, active_status)
    """
    max_name_length = max(len(channel[0]) for channel in channels)
    max_index_length = len(str(len(channels)))

    for i, (name, url, active) in enumerate(channels, 1):
        status = "Y" if active else "N"
        padded_index = str(i).rjust(max_index_length)
        padded_name = name.ljust(max_name_length)
        print(f"{padded_index}. [{status}] {padded_name} {url}")


def toggle_channel(channels, index):
    """
    Toggle the active status of a channel.

    Args:
    channels (list): List of tuples containing (channel_name, channel_url, active_status)
    index (int): Index of the channel to toggle
    """
    if 1 <= index <= len(channels):
        name, url, active = channels[index - 1]
        channels[index - 1] = (name, url, not active)
        print("-" * 58)
        print(f"Toggled channel: {name}")
        print("-" * 58)
    else:
        print("Invalid index")


def toggle_all_channels(channels, state):
    """
    Toggle the active status of all channels.

    Args:
    channels (list): List of tuples containing (channel_name, channel_url, active_status)
    state (bool): New active status for all channels
    """
    for i in range(len(channels)):
        channels[i] = (channels[i][0], channels[i][1], state)
    print("-" * 58)
    print(f"{'Activated' if state else 'Deactivated'} all channels")
    print("-" * 58)


def wait_for_login(driver):
    """
    Wait for the user to log in to YouTube by checking for either:
    1. Presence of avatar button
    2. Absence of sign-in button
    """
    print("Please log in to your YouTube account in the opened browser window.")
    print("Note: You only need to log in for this session, not to Chrome itself.")

    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            # Wait for page load with longer timeout
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "ytd-masthead"))
            )

            # Check for avatar button
            try:
                avatar = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "button#avatar-btn")
                    )
                )
                if avatar.is_displayed():
                    print("Login detected via avatar. Proceeding...")
                    return True
            except TimeoutException:
                # If no avatar found after timeout, ask user
                retries += 1
                choice = input(
                    f"\nLogin not detected (attempt {retries}/{max_retries}). Enter 'r' to retry or 'q' to quit: "
                )
                if choice.lower() == "q":
                    return False
                driver.refresh()
                time.sleep(2)
                continue

        except Exception as e:
            print(f"Error checking login status: {str(e)}")
            retries += 1
            time.sleep(2)

    print("Maximum retry attempts reached. Please try again later.")
    return False


def wait_for_channels_page(driver):
    """
    Wait for the channels page to fully load.
    """
    try:
        # Wait for channel elements to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "ytd-channel-renderer"))
        )
        # Wait a bit more for dynamic content
        time.sleep(2)
        return True
    except TimeoutException:
        print("Could not detect channel elements on the page.")
        return False


def save_channels_page(driver):
    """
    Automatically save the channels page HTML.
    """
    try:
        # Get the page source after waiting for content
        html_content = driver.page_source

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


def main():
    print("\n" + "-" * 58)
    print("Welcome to YouTubeTransfer!")
    print("-" * 58)

    # Check for existing YouTube.html file
    downloads_dir = os.path.expanduser("~/Downloads")
    existing_file = os.path.join(downloads_dir, "YouTube.html")

    if os.path.exists(existing_file):
        print(f"\nFound existing channels file: {existing_file}")
        print("Last modified: ", time.ctime(os.path.getmtime(existing_file)))

        while True:
            choice = (
                input("\nUse existing file? (Y)es, (N)ew, or (Q)uit: ").strip().upper()
            )

            if choice == "Q":
                print("Exiting program.")
                return
            elif choice in ["Y", "N"]:
                break
            print("Invalid choice. Please try again.")

        if choice == "Y":
            print("\nUsing existing channels file...")
            channels = extract_channels(existing_file)
            if not channels:
                print("No channels found in file. Please generate a new one.")
                return
        else:
            print("\nGenerating new channels file...")
            channels = None  # Will be set later if we successfully get new data
    else:
        print("\nNo existing channels file found. Will generate new one.")
        choice = "N"
        channels = None

    if choice == "N":
        try:
            driver = get_secure_driver()  # Use secure driver here

            # Go to YouTube and wait for login
            driver.get("https://www.youtube.com")
            if not wait_for_login(driver):
                driver.quit()
                return

            # Navigate to channels page
            print("\nNavigating to channels page...")
            driver.get("https://www.youtube.com/feed/channels")

            # Wait for the page to load and save it
            if wait_for_channels_page(driver):
                file_path = save_channels_page(driver)
                if file_path and os.path.exists(file_path):
                    print("Successfully saved channels page. Processing channels...")
                    channels = extract_channels(file_path)
                    print("\nFirst phase complete. Closing browser...")
                    driver.quit()  # Explicitly close the first session
                else:
                    print("Failed to save channels page.")
                    driver.quit()
                    return
            else:
                print("Failed to load channels page.")
                driver.quit()
                return

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Ensure Google Chrome is installed")
            print("2. Ensure ChromeDriver is installed and matches your Chrome version")
            if "driver" in locals():
                driver.quit()
            return

    if channels:
        print("\nStarting subscription phase...")
        # Menu loop
        while True:
            display_channels(channels)
            print("-" * 58)
            print("\nOptions:")
            print("A) Toggle all to Activate")
            print("D) Toggle all to Deactivate")
            print("Enter an index to toggle a specific channel")
            print("C) Continue")

            choice = input("\nEnter your choice: ").strip().upper()

            if choice == "A":
                toggle_all_channels(channels, True)
            elif choice == "D":
                toggle_all_channels(channels, False)
            elif choice == "C":
                break
            else:
                try:
                    index = int(choice)
                    toggle_channel(channels, index)
                except ValueError:
                    print("Invalid input. Please try again.")

        # After breaking from the menu loop, proceed with subscriptions
        total, already, new = subscribe_to_channels(channels)
        print(f"\nSubscription Summary:")
        print(f"Total channels processed: {total}")
        print(f"Already subscribed: {already}")
        print(f"New subscriptions: {new}")


if __name__ == "__main__":
    main()
