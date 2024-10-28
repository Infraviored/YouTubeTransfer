from channel_extractor import ChannelExtractor
from channel_subscriber import ChannelSubscriber
import os
import time


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
            extractor = ChannelExtractor()
            channels = extractor.extract_channels(existing_file)
            if not channels:
                print("No channels found in file. Please generate a new one.")
                return
        else:
            print("\nGenerating new channels file...")
            channels = None
    else:
        print("\nNo existing channels file found. Will generate new one.")
        choice = "N"
        channels = None

    if choice == "N":
        try:
            extractor = ChannelExtractor()
            channels = extractor.get_channel_list()

            if not channels:
                print("Failed to get channel list. Please try again.")
                return

        except Exception as e:
            print(f"\nError: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Ensure Google Chrome is installed")
            print("2. Ensure ChromeDriver is installed and matches your Chrome version")
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
        subscriber = ChannelSubscriber()
        total, already, new = subscriber.subscribe_to_channels(channels)
        print(f"\nSubscription Summary:")
        print(f"Total channels processed: {total}")
        print(f"Already subscribed: {already}")
        print(f"New subscriptions: {new}")


def display_channels(channels):
    """Display the list of channels in a formatted manner."""
    max_name_length = max(len(channel[0]) for channel in channels)
    max_index_length = len(str(len(channels)))

    for i, (name, url, active) in enumerate(channels, 1):
        status = "Y" if active else "N"
        padded_index = str(i).rjust(max_index_length)
        padded_name = name.ljust(max_name_length)
        print(f"{padded_index}. [{status}] {padded_name} {url}")


def toggle_channel(channels, index):
    """Toggle the active status of a channel."""
    if 1 <= index <= len(channels):
        name, url, active = channels[index - 1]
        channels[index - 1] = (name, url, not active)
        print("-" * 58)
        print(f"Toggled channel: {name}")
        print("-" * 58)
    else:
        print("Invalid index")


def toggle_all_channels(channels, state):
    """Toggle the active status of all channels."""
    for i in range(len(channels)):
        channels[i] = (channels[i][0], channels[i][1], state)
    print("-" * 58)
    print(f"{'Activated' if state else 'Deactivated'} all channels")
    print("-" * 58)


if __name__ == "__main__":
    main()
