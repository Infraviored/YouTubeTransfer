import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time

def extract_channels(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    channel_renderers = soup.find_all('ytd-channel-renderer')

    channels = []
    for renderer in channel_renderers:
        link = renderer.find('a', class_='channel-link')
        if link:
            channel_url = link['href']
            # Extract channel name from the URL
            channel_name = channel_url.split('@')[-1]
            if channel_url.startswith('/'):
                channel_url = 'https://www.youtube.com' + channel_url
            channels.append((channel_name, channel_url, True))  # True for initially active


    return channels

def display_channels(channels):
    max_name_length = max(len(channel[0]) for channel in channels)
    max_index_length = len(str(len(channels)))

    for i, (name, url, active) in enumerate(channels, 1):
        status = "Y" if active else "N"
        padded_index = str(i).rjust(max_index_length)
        padded_name = name.ljust(max_name_length)
        print(f"{padded_index}. [{status}] {padded_name} {url}")

def toggle_channel(channels, index):
    if 1 <= index <= len(channels):
        name, url, active = channels[index - 1]
        channels[index - 1] = (name, url, not active)
        print(f"Toggled channel: {name}")
    else:
        print("Invalid index")

def wait_for_login(driver):
    print("Please log in to your YouTube account in the opened browser window.")
    print("Note: You only need to log in for this session, not to Chrome itself.")
    while True:
        try:
            # Wait for the avatar image to be visible, which indicates a successful login
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

def subscribe(driver):
    try:
        # Wait for the button element to be present (Subscribe or Subscribed)
        subscribe_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content')]"))
        )
        
        # Ensure the button is visible before checking text
        WebDriverWait(driver, 5).until(EC.visibility_of(subscribe_button))

        # Adding a short delay to ensure the text is fully loaded
        time.sleep(2)  # Small delay to allow text content to load

        # Fetching button text
        button_text = subscribe_button.text.strip().lower()

        # If text is still empty, try retrieving via JavaScript
        if not button_text:
            print("Retrieving button text via JavaScript...")
            button_text = driver.execute_script("return arguments[0].textContent;", subscribe_button).strip().lower()

        print(f"Detected button text: '{button_text}'")

        # If it's "subscribe", click the button to subscribe
        if button_text == "subscribe":
            driver.execute_script("arguments[0].click();", subscribe_button)
            print("Subscribed successfully using Method 1")
            return True
        
        # If it's "subscribed", we skip since the channel is already subscribed
        elif button_text == "subscribed":
            print("Already subscribed.")
            return False

        # Handle any unexpected button text
        print(f"Unexpected button text: '{button_text}'")
        return False

    except TimeoutException:
        print("Button not found in time.")
        return False



def subscribe_to_channels(channels):
    driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed and in PATH
    driver.get("https://www.youtube.com")

    
    if not wait_for_login(driver):
        driver.quit()
        return

    for name, url, active in channels:
        if active:
            print(f"Attempting to subscribe to: {name}")
            driver.get(url)

            # Try subscribing using the three methods in order
            success = subscribe(driver)
            if success:
                print(f"Successfully subscribed to: {name}")
            else:
                print(f"Failed or already subscribed to: {name}")

        time.sleep(1)  # Simulate delay between subscriptions
    
    driver.quit()

# def subscribe(driver):
#     try:
#         # Long wait for the presence of the general button
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content')]"))
#         )
#         print("Found 'Subscribe' button, determining its state...")

#         # Short wait to check for "Subscribe" button
#         subscribe_button = WebDriverWait(driver, 1).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and text()='Subscribe']"))
#         )
        
#         if subscribe_button:
#             print("Found 'Subscribe' button, subscribing now...")
#             # Scroll to the element to ensure it's within view
#             driver.execute_script("arguments[0].scrollIntoView(true);", subscribe_button)
#             # Wait a bit to ensure the button is visible and not covered
#             WebDriverWait(driver, 1).until(EC.element_to_be_clickable(subscribe_button))
#             driver.execute_script("arguments[0].click();", subscribe_button)
#             print("Subscribed successfully!")
#             return True
#     except TimeoutException:
#         print("No 'Subscribe' button found, checking for 'Subscribed' button.")

#     try:
#         # Short wait to check for "Subscribed" button
#         subscribed_button = WebDriverWait(driver, 1).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and text()='Subscribed']"))
#         )
        
#         if subscribed_button:
#             print("Already subscribed.")
#             return False
#     except TimeoutException:
#         print("Neither 'Subscribe' nor 'Subscribed' buttons found.")

#     return False


def subscribe2(driver):
    try:
        # Long wait for the presence of the general button
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content')]"))
        )
        print("Found 'Subscribe' button, determining its state...")

        # Short wait to check for "Subscribe" button
        subscribe_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and text()='Subscribe']"))
        )
        
        if subscribe_button:
            print("Found 'Subscribe' button, subscribing now...")
            driver.execute_script("arguments[0].click();", subscribe_button)
            return True
    except TimeoutException:
        print("No 'Subscribe' button found, checking for 'Subscribed' button.")

    try:
        # Short wait to check for "Subscribed" button
        subscribed_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'yt-spec-button-shape-next__button-text-content') and text()='Subscribed']"))
        )
        
        if subscribed_button:
            print("Already subscribed.")
            return False
    except TimeoutException:
        print("Neither 'Subscribe' nor 'Subscribed' buttons found.")

    return False


def test_subscribe_to_channels(channels):
    print("Starting fake subscription process...")
    driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH
    driver.get("https://www.youtube.com")
    
    if not wait_for_login(driver):
        driver.quit()
        return

    for name, url, active in channels:
        if active:
            print(f"Attempting to subscribe to: {name}")
            driver.get(url)
            time.sleep(5)  # Allow the page to load

            # Try subscribing using the three methods in order
            success = subscribe(driver)
            if success:
                print(f"Successfully subscribed to: {name}")
            else:
                print(f"Failed or already subscribed to: {name}")

        time.sleep(2)  # Simulate delay between subscriptions
    input("continue")

    print("Fake subscription process completed.")
    driver.quit()



def main():
    # channels = [("Muse", "https://www.youtube.com/@promptmuse", True)]
    # test_subscribe_to_channels(channels)
    print("Welcome to YouTubeTransfer!")
    print("Log in with the old user account in browser.")
    print("Go to https://www.youtube.com/feed/channels")
    print("Press Ctrl+S to save the page on your system.")

    # file_path = input("Provide the filepath of the saved HTML file: ")
    file_path = "/home/schneider/Downloads/YouTube.html"
    channels = extract_channels(file_path)

    while True:
        display_channels(channels)
        print("\nOptions:")
        print("A) Toggle all to Activate")
        print("N) Toggle all to Deactivate")
        print("Enter an index to toggle a specific channel")
        print("C) Continue")

        choice = input("Enter your choice: ").strip().lower()

        if choice == 'a':
            channels = [(name, url, True) for name, url, _ in channels]
        elif choice == 'n':
            channels = [(name, url, False) for name, url, _ in channels]
        elif choice == 'c':
            break
        elif choice.isdigit():
            toggle_channel(channels, int(choice))
        else:
            print("Invalid choice. Please try again.")

    subscribe_to_channels(channels)

if __name__ == "__main__":
    main()