FROM python:3.12-slim

WORKDIR /app

# Create the /config directory
RUN mkdir -p /config

# Copy the application files
COPY app/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for the config directory
ENV CONFIG_DIR=/config

# Add an entrypoint script to handle config initialization
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint and command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"]