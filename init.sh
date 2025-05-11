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
    print('Connected to Lidarr API.')
    exit(0)
except requests.exceptions.RequestException as e:
    print('Lidarr API not available. Retrying in 10 seconds...')
    exit(1)
" ; then
            break
        else
            echo "Lidarr API not available. Retrying in 10 seconds..."
            sleep 10
        fi
    done
}

while true; do
    if [ -f "$LOCK_FILE" ]; then
        echo "Script is already running. Waiting for the next run..."
    else
        check_lidarr_api

        touch "$LOCK_FILE"
        echo "Scanning Lidarr..."
        /bin/sh /app/run_spotdl.sh
        
        rm "$LOCK_FILE"
    fi
    echo "Next Lidarr scan at:"
    date -d "now + ${MINUTE_INTERVAL} minutes"
    
    sleep $((MINUTE_INTERVAL * 60))
done
