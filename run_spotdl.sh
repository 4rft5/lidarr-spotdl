#!/bin/sh
LOGFILE="/logs/run_spotdl.log"

if [ ! -d "/logs" ]; then
    mkdir -p /logs
    chmod 777 /logs
    touch $LOGFILE
fi

DOWNLOAD_DIR="${DOWNLOAD_DIR:-/downloads/music}"

echo "$(date): Starting Download (if possible)..." | tee -a $LOGFILE
downloaded_directories=$(python /app/extract_spotify_urls.py --download-dir $DOWNLOAD_DIR 2>&1)

if [ $? -ne 0 ]; then
    echo "$(date): Error running extract_spotify_urls.py. Exiting." | tee -a $LOGFILE
    exit 1
fi

echo "$(date): $downloaded_directories" | tee -a $LOGFILE
