# Crawler Notifier

Crawler Notifier is an application designed to crawl forums and notify users based on keyword triggers. It is highly configurable and supports multiple notification methods.

## Features
- Crawl forums for specific keywords.
- Notify users via email and Telegram.
- Configurable settings for keywords, notification methods, and more.
- Tracks visited threads to avoid duplicate notifications.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/machineglow/crawler-notifier.git
   cd crawler-notifier
   ```
2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

## Usage
1. Configure the application by editing `config/config.yaml`.
2. Run the application:
   ```bash
   python app/main.py
   ```

## Configuration
- `config/config.yaml`: Main configuration file for keywords, notification settings, etc.
- `config/seen.json` and `config/visited_threads.json`: Track seen and visited threads.

## Advanced Configuration

These BeautifulSoap CSS selector parameters determine how to detect "Threads" in the target HTML and "Posts" when in the thread.  This has been pre-populated with RFD specific parameters

- `THREAD_LIST_ITEM_SELECTOR`: "a.thread_title_link"              # Each thread container
- `THREAD_TITLE_SELECTOR`: "a.thread_title_link"        # Thread URL link inside thread container
- `THREAD_UNIQUE_ID_ATTR`: "data-thread-id"            # Attribute on li.topic for thread ID
- `POST_CONTAINER_SELECTOR`: "section.thread_posts"
- `POST_BODY_SELECTOR`: "div.content"
- `NEXT_PAGE_SELECTOR`: "a[rel='next']"


## Environment Variables

The following environment variables are used in `config.yaml`:

- `CONFIG_DIR`: Directory where config.yaml is found
- `TELEGRAM_BOT_TOKEN`: Token for the Telegram bot used for notifications.
- `TELEGRAM_CHAT_ID`: Chat ID for the Telegram bot to send messages to.
- `EMAIL_SENDER`: Email address used as the sender for email notifications.
- `EMAIL_PASSWORD`: Password for the sender email account.
- `EMAIL_RECIPIENT`: Email address to receive notifications.

Ensure these variables are set in your environment before running the application.

## Dependencies
- `requests`
- `beautifulsoup4`
- `pyyaml`
- `feedparser`

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
