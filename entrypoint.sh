#!/bin/bash

CONFIG_FILE="$CONFIG_DIR/config.yaml"
TEMPLATE_FILE="config-TEMPLATE.yaml"

# Check if template exists; if not, copy from config-TEMPLATE.yaml
if [ ! -f "$CONFIG_DIR/$TEMPLATE_FILE" ]; then
    echo "config-TEMPLATE.yaml not found. Creating config-TEMPLATE.yaml..."
    cp "$TEMPLATE_FILE" "$CONFIG_DIR/$TEMPLATE_FILE"
fi

# Check if config.yaml exists; if not, copy from config-TEMPLATE.yaml
if [ ! -f "$CONFIG_FILE" ]; then
    echo "config.yaml not found. Copying config-TEMPLATE.yaml..."
    cp "$TEMPLATE_FILE" "$CONFIG_DIR/$TEMPLATE_FILE"
fi

# Execute the main command
exec "$@"