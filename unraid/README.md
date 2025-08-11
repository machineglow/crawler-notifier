# Crawler Notifier

Crawler Notifier is an application designed to crawl forums and notify users based on keyword triggers. It is highly configurable and supports multiple notification methods.

## Features
- Crawl forums for specific keywords.
- Notify users via email and Telegram.
- Configurable settings for keywords, notification methods, and more.
- Tracks visited threads to avoid duplicate notifications.

## Installation
1. Import docker template:
   ```bash
   cp my-crawler-notifier.xml /boot/config/plugins/dockerMan/templates-user/ 
   ```

2. Setup Notification Settings
   - Telegram:
      1. Create your own Telegram bot and get it's telegram bot ID
      2. Create a new chat between the bot and your desired recipient telegram account by messaging it
      3. Find out your telegram CHAT ID by searching for @userinfobot and clicking "start"

   - Email:
      1. Figure out your SMTP email server hostname
      2. Figure out your SMTP server port

3. Create docker container: Unraid GUI -> docker -> Add Container -> select crawler-notifier from User Templates
   - Map the CONFIG_DIR to your desired configuration directory (/mnt/user/appData/crawler-notifier)
   - Plug in the Telegram Bot Token in the TELEGRAM_BOT_TOKEN variable in template
   - Plug in the CHAT ID to the TELEGRAM_CHAT_ID variable in template
   - Plug in your email username to EMAIL_SENDER variable in template
   - Plug in your email password to EMAIL_PASSWORD variable in template
   - Plug in your email to EMAIL_RECIPIENT variable in template

4. After container starts up, edit the config.yaml created in your CONFIG_DIR
   1. Update watch section:
      - keywords: [ "comma", "delimited", "list", "of", "keywords" ]
      - search_body: boolean (search thread posts for keywords)
      - max_forum_pages: int (number of pages of threads to crawl at each time)
      - max_thread_pages: DEPRECATED
   2. Update notify section:
      - If using email:
         - enabled: true
         - smtp_server: EMAIL_SERVER
         - port: EMAIL_PORT
      - If using telegram 
         - enabled: true
   3. Update interval_minutes
      - Don't go lower than 5-10 minutes or else you may hit rate limits
   
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
