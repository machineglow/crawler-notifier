#!/bin/bash
# filepath: /Users/myk/Documents/GitHub/crawler-notifier/entrypoint.sh

CONFIG_FILE="$CONFIG_DIR/config.yaml"
TEMPLATE_FILE="$CONFIG_DIR/config-TEMPLATE.yaml"

# Check if config.yaml exists; if not, copy from config-TEMPLATE.yaml
if [ ! -f "$CONFIG_FILE" ]; then
    echo "config.yaml not found. Creating from config-TEMPLATE.yaml..."
    cp "$TEMPLATE_FILE" "$CONFIG_FILE"
fi

# Execute the main command
exec "$@"