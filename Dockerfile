# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install any needed packages and dependencies
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
RUN pip install spotdl requests yt-dlp ytmusicapi
RUN spotdl --download-ffmpeg

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the necessary scripts and make them executable
COPY run_spotdl.sh /app/run_spotdl.sh
RUN chmod +x /app/run_spotdl.sh

COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh
CMD ["/app/init.sh"]