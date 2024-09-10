import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Configuration
BUTTON_WAIT_TIME = 10  # Seconds to wait for button to appear
PAGE_LOAD_WAIT_TIME = 3  # Seconds to wait after page load before checking for button
DELAY_BETWEEN_CHANNELS = 1  # Seconds to wait between processing channels

# Old configuration (comment out the above and uncomment below to use old timings)
# BUTTON_WAIT_TIME = 15
# PAGE_LOAD_WAIT_TIME = 5
# DELAY_BETWEEN_CHANNELS = 2

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='youtube_subscription.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_button(driver):
    """
    Wait for the subscribe button to be present on the page.
    
    Args:
    driver (webdriver): Selenium webdriver instance
    
    Returns:
    bool: True if button is found, False otherwise
    """
    button_xpath = "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and (translate(text(), 'SUBSCRIBE', 'subscribe')='subscribe' or translate(text(), 'SUBSCRIBE', 'subscribe')='subscribed')]"
    try:
        WebDriverWait(driver, BUTTON_WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )
        return True
    except TimeoutException:
        return False

def subscribe(driver, channel_name):
    """
    Attempt to subscribe to a YouTube channel.
    
    Args:
    driver (webdriver): Selenium webdriver instance
    channel_name (str): Name of the channel to subscribe to
    
    Returns:
    int: 0 if already subscribed, 1 if newly subscribed, -1 if failed
    """
    button_xpath = "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and (translate(text(), 'SUBSCRIBE', 'subscribe')='subscribe' or translate(text(), 'SUBSCRIBE', 'subscribe')='subscribed')]"
    
    try:
        button = driver.find_element(By.XPATH, button_xpath)
        button_text = button.text.strip().lower()
        print(f"Detected Text '{button_text}'")
        
        if button_text == "subscribe":
            print("Subscribing")
            driver.execute_script("arguments[0].click();", button)
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

def subscribe_to_channels(channels):
    """
    Subscribe to a list of YouTube channels.
    
    Args:
    channels (list): List of tuples containing (channel_name, channel_url, active_status)
    
    Returns:
    tuple: (total_processed, already_subscribed, new_subscriptions)
    """
    driver = webdriver.Chrome()
    driver.get("https://www.youtube.com")
    
    if not wait_for_login(driver):
        driver.quit()
        return 0, 0, 0

    total_processed = 0
    already_subscribed = 0
    new_subscriptions = 0
    active_channels = [channel for channel in channels if channel[2]]
    total_active = len(active_channels)

    for i, (name, url, _) in enumerate(active_channels, 1):
        print("\n"+"-"*58)
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
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    channel_renderers = soup.find_all('ytd-channel-renderer')

    channels = []
    for renderer in channel_renderers:
        link = renderer.find('a', class_='channel-link')
        if link:
            channel_url = link['href']
            channel_name = channel_url.split('@')[-1]
            if channel_url.startswith('/'):
                channel_url = 'https://www.youtube.com' + channel_url
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
        print("-"*58)
        print(f"Toggled channel: {name}")
        print("-"*58)
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
    print("-"*58)
    print(f"{'Activated' if state else 'Deactivated'} all channels")
    print("-"*58)


def wait_for_login(driver):
    """
    Wait for the user to log in to YouTube.
    
    Args:
    driver (webdriver): Selenium webdriver instance
    
    Returns:
    bool: True if login is successful, False otherwise
    """
    print("Please log in to your YouTube account in the opened browser window.")
    print("Note: You only need to log in for this session, not to Chrome itself.")
    while True:
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//img[@id='img' and @alt='Avatar image']"))
            )
            print("Login detected. Proceeding with subscriptions.")
            return True
        except TimeoutException:
            choice = input("Login not detected. Enter 'r' to retry or 'q' to quit: ")
            if choice.lower() == 'q':
                return False
        time.sleep(1)

def main():
    print("\n"+"-"*58)
    print("Welcome to YouTubeTransfer!")
    print("-"*58)
    print("Log in with the old user account in browser.")
    print("Go to https://www.youtube.com/feed/channels")
    print("Press Ctrl+S to save the page on your system.")

    # file_path = input("Provide the filepath of the saved HTML file: ")
    file_path = "/home/schneider/Downloads/YouTube.html"
    channels = extract_channels(file_path)
    print("\n"+"-"*58)

    while True:

        display_channels(channels)
        print("-"*58)
        print("\nOptions:")
        print("A) Toggle all to Activate")
        print("D) Toggle all to Deactivate")
        print("Enter an index to toggle a specific channel")
        print("C) Continue")

        choice = input("Enter your choice: ").strip().lower()

        if choice == 'a':
            toggle_all_channels(channels, True)
        elif choice == 'd':
            toggle_all_channels(channels, False)
        elif choice == 'c':
            break
        elif choice.isdigit():
            toggle_channel(channels, int(choice))
        else:
            print("Invalid choice. Please try again.")

    total, already, new = subscribe_to_channels(channels)
    
    print("\n"+"-"*58)
    print("Subscription Process Completed")
    print(f"Total channels processed: {total}")
    print(f"Already subscribed: {already}")
    print(f"New subscriptions: {new}")
    print("-"*58)

if __name__ == "__main__":
    main()