#!/bin/sh
LOGFILE="/logs/run_spotdl.log"
INPUT_QUEUE="/app/input_queue.txt"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-/music}"

if [ ! -d "/logs" ]; then
    mkdir -p /logs
    chmod 777 /logs
    touch $LOGFILE
fi

if [ -f "$INPUT_QUEUE" ]; then
    rm -f $INPUT_QUEUE
fi

touch $INPUT_QUEUE
chmod 777 $INPUT_QUEUE

echo " " | tee -a $LOGFILE
echo "$(date): Attempting Search and Download... (This may take a while!)" | tee -a $LOGFILE
echo " " | tee -a $LOGFILE
downloaded_directories=$(python /app/extract_spotify_urls.py --download-dir $DOWNLOAD_DIR 2>&1)

if [ $? -ne 0 ]; then
    echo "$(date): Error running extract_spotify_urls.py. Exiting." | tee -a $LOGFILE
    exit 1
fi