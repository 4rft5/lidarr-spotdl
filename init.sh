#!/bin/sh

TZ="${TZ:-UTC}"
export TZ

LOCK_FILE="/tmp/spotdl.lock"

check_lidarr_api() {
    while true; do
        if python3 -c "
import requests
try:
    response = requests.get('$LIDARR_URL/api/v1/system/status?apiKey=$LIDARR_API_KEY')
    response.raise_for_status()
    print(' ')
    print('Connected to Lidarr API.')
    exit(0)
except requests.exceptions.RequestException as e:
    print(f'Error: {e}.')
    exit(1)
" ; then
            break
        else
            echo " "
            echo "Lidarr API not available. Retrying in 10 seconds..."
            sleep 10
        fi
    done
}

start_import() {
    echo "Starting Lidarr import..."
    echo " "

    python /app/lidarr_import.py $downloaded_directories
}

while true; do
    if [ -f "$LOCK_FILE" ]; then
        echo "Script is already running. Waiting for the next run..."
    else
        check_lidarr_api

        touch "$LOCK_FILE"
        echo "Scanning Lidarr and beginning download...(This may take a while!)"
        echo " "

        downloaded_directories=$(/bin/sh /app/run_spotdl.sh)

        if [ -n "$downloaded_directories" ]; then
            echo "Downloaded the following:"
            cat /app/input_queue.txt
            echo " "
            start_import
        else
            echo "No new directories to import."
        fi

        rm "$LOCK_FILE"
    fi
    echo " "
    echo "Next Lidarr scan at:"
    date -d "now + ${MINUTE_INTERVAL} minutes"
    
    sleep $((MINUTE_INTERVAL * 60))
done
