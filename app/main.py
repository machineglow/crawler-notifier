import os
import sys
import time
import yaml
import logging

import storage
import watcher
import notifiers

logger = logging.getLogger()

def get_config_dir():
    # Use CONFIG_DIR env if set, else use ./config (relative to script)
    env_dir = os.environ.get('CONFIG_DIR')
    logger.info(f"Using config directory: {env_dir if env_dir else './config'}")
    if env_dir:
        return os.path.normpath(env_dir)
    # Default to ./config relative to this file
    return os.path.join(os.path.dirname(__file__), '..', 'config')

CONFIG_DIR = get_config_dir()
CONFIG_PATH = os.path.normpath(os.path.join(CONFIG_DIR, "config.yaml"))

def resolve_env_vars(config):
    """Recursively replace placeholders with environment variable values."""
    if isinstance(config, dict):
        return {k: resolve_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [resolve_env_vars(v) for v in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        env_var = config[2:-1]
        return os.environ.get(env_var, "")
    return config

def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error in config file: {e}")

    if not isinstance(config, dict):
        raise ValueError("Config file root element must be a dictionary.")

    # Resolve environment variables
    config = resolve_env_vars(config)

    debug = config.get("debug", False)
    if not isinstance(debug, bool):
        raise ValueError("The 'debug' flag must be boolean.")

    watch = config.get("watch")
    if not isinstance(watch, list) or not watch:
        raise ValueError("Missing or invalid 'watch' section.")

    notify = config.get("notify")
    if not isinstance(notify, dict):
        raise ValueError("Missing or invalid 'notify' section.")

    interval = config.get("interval_minutes", 10)
    if not isinstance(interval, int) or interval <= 0:
        raise ValueError("'interval_minutes' must be positive integer.")

    persistence = config.get("persistence", {})
    if not isinstance(persistence, dict):
        raise ValueError("'persistence' must be dictionary.")

    seen_file = persistence.get("seen_file", "seen.csv")
    visited_threads_file = persistence.get("visited_threads_file", "visited_threads.csv")

    if not isinstance(seen_file, str) or not seen_file.strip():
        raise ValueError("Invalid 'seen_file' in persistence.")
    if not isinstance(visited_threads_file, str) or not visited_threads_file.strip():
        raise ValueError("Invalid 'visited_threads_file' in persistence.")

    config["debug"] = debug
    config["interval_minutes"] = interval
    config.setdefault("persistence", {})["seen_file"] = seen_file
    config["persistence"]["visited_threads_file"] = visited_threads_file

    return config

def setup_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger()

def notify_services(message, config):
    logger.info(f"Sending notification: {message}")
    for notifier_name in ["telegram", "email"]:
        notifier_cfg = config["notify"].get(notifier_name)
        if notifier_cfg and notifier_cfg.get("enabled"):
            try:
                notifiers.send_notification(notifier_name, message, notifier_cfg)
                logger.debug(f"{notifier_name.capitalize()} notification sent successfully.")
            except Exception as e:
                logger.error(f"Error sending {notifier_name} notification: {e}")

def main():
    try:
        config = load_config(CONFIG_PATH)
    except (FileNotFoundError, ValueError) as e:
        print(f"[CONFIG ERROR] {e}")
        sys.exit(1)

    global logger
    logger = setup_logging(config["debug"])

    seen_file = os.path.join(CONFIG_DIR, config["persistence"]["seen_file"])
    visited_threads_file = os.path.join(CONFIG_DIR, config["persistence"]["visited_threads_file"])

    seen = storage.load_csv_set(seen_file)
    visited_threads = storage.load_csv_set(visited_threads_file)

    logger.info("Starting RFD keyword watcher service...")
    try:
        while True:
            logger.debug("Checking feeds and pages for keywords...")
            found_msgs = watcher.check_for_keywords(config, seen, visited_threads)
            if found_msgs:
                logger.info(f"Found {len(found_msgs)} new matching entries.")
                for msg in found_msgs:
                    notify_services(msg, config)
                storage.save_csv_set(seen, seen_file)
                storage.save_csv_set(visited_threads, visited_threads_file)
                logger.debug("Updated seen entries and visited threads saved.")
            else:
                logger.debug("No new matching entries found this cycle.")
            time.sleep(config["interval_minutes"] * 60)
    except KeyboardInterrupt:
        logger.info("Shutdown requested, saving state and exiting...")
        storage.save_csv_set(seen, seen_file)
        storage.save_csv_set(visited_threads, visited_threads_file)
        logger.info("State saved. Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        storage.save_csv_set(seen, seen_file)
        storage.save_csv_set(visited_threads, visited_threads_file)
        logger.info("State saved before exit due to error.")

if __name__ == "__main__":
    main()
