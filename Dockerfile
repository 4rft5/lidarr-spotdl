# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download FFmpeg and clean up any unnecessary files
RUN spotdl --download-ffmpeg && \
    rm -rf /path/to/temp/files  # Adjust path as necessary

# Copy the necessary application files
COPY . /app

# Copy and make scripts executable
COPY run_spotdl.sh /app/run_spotdl.sh
RUN chmod +x /app/run_spotdl.sh

COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# Default command to run the application
CMD ["/app/init.sh"]
