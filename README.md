# YouTubeTransfer

Effortlessly migrate your YouTube subscriptions when switching to a more affordable Premium account.

## Why Use YouTubeTransfer?

- **Significant Cost Savings**: 
  - German YouTube Premium: €155.88/year (€12.99/month)
  - Turkish YouTube Premium: Approximately €22/year
  - **Annual Savings**: €133.88 (85.9% reduction)

- **Easy Access to Affordable Accounts**: 
  - Purchase fresh Turkish YouTube Premium accounts from platforms like [Kinguin](https://www.kinguin.net/)
  - Note: These are new accounts, requiring an annual switch

- **Preserve Your YouTube Experience**:
  - Automatically transfer all your subscribed channels to the new account
  - Avoid the tedious process of manually resubscribing to potentially hundreds of channels
  - Ensure you don't miss content from your favorite creators after switching accounts

- **Hassle-Free Annual Transition**:
  - Streamline the yearly account switch process
  - Save hours of manual work and potential oversights
  - Maintain your personalized YouTube ecosystem effortlessly

- **Flexible Channel Selection**:
  - Choose which channels to transfer
  - Opportunity to curate your subscriptions during the transfer process

By using YouTubeTransfer, you can take advantage of more affordable YouTube Premium options without sacrificing your carefully curated subscription list. The tool automates an otherwise time-consuming and error-prone process, making the annual account switch a breeze rather than a chore.

## Features

- Fast and efficient subscription transfer
- Secure operation (doesn't store login information)
- Visual feedback on subscription progress
- Option to choose which channels to transfer

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the script:
   ```
   python ytt.py
   ```
3. Follow on-screen instructions to transfer your subscriptions.

## Detailed Guide

### Prerequisites

- Python 3.6+
- Chrome browser
- ChromeDriver (matching your Chrome version)

### Installation

#### Linux

1. Install Python and pip:
   ```
   sudo apt-get update && sudo apt-get install python3 python3-pip
   ```
2. Clone the repository:
   ```
   git clone https://github.com/yourusername/YouTubeTransfer.git
   cd YouTubeTransfer
   ```
3. Set up a virtual environment (optional):
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Install Chrome and ChromeDriver (if not already installed).

#### Windows

1. Install Python from the [official website](https://www.python.org/downloads/).
2. Download and extract the repository.
3. Set up a virtual environment (optional):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install required packages:
   ```
   pip install -r requirements.txt
   ```
5. Install Chrome and ChromeDriver (if not already installed).

### Usage

1. Run `python ytt.py`
2. Log in to your old YouTube account in the opened browser.
3. Save your subscriptions page (https://www.youtube.com/feed/channels) locally.
4. Provide the saved HTML file path when prompted.
5. Review and select channels to transfer.
6. Log in to your new YouTube account when prompted.
7. Wait for the transfer process to complete.

## Troubleshooting

- Ensure ChromeDriver version matches your Chrome browser version.
- Adjust `BUTTON_WAIT_TIME` and `PAGE_LOAD_WAIT_TIME` in `ytt.py` if needed.
- Check `youtube_subscription.log` for detailed error messages.

## Contributing

Contributions are welcome! Please submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
