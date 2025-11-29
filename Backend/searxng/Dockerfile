# Custom SearXNG image with learning platform filter plugin
FROM searxng/searxng:latest

# Copy custom plugin to SearXNG plugins directory
COPY learning_platform_filter.py /usr/local/searxng/searx/plugins/learning_platform_filter.py

# Ensure proper permissions
USER root
RUN chmod 644 /usr/local/searxng/searx/plugins/learning_platform_filter.py
USER searxng
