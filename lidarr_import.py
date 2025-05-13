import os
import requests

def import_downloaded_tracks(downloaded_directories):
    lidarr_url = os.getenv("LIDARR_URL", "http://your-lidarr-ip:port")
    api_key = os.getenv("LIDARR_API_KEY", "your-lidarr-api-key")

    for directory in downloaded_directories:
        print(f"Attempting import for directory: {directory}")
        get_url = f"{lidarr_url}/api/v1/manualimport?apiKey={api_key}&folder={directory}&filterExistingFiles=true&replaceExistingFiles=false"
        response_get = requests.get(get_url)

        if response_get.status_code == 200:
            data_to_post = response_get.json()
            print(f"Retrieved data for {directory}")
        else:
            print(f"Error retrieving data for {directory}: {response_get.status_code} {response_get.text}")
            continue

        if not data_to_post:
            print(f"No data found for {directory}.")
            continue

        for entry in data_to_post:
            post_url = f"{lidarr_url}/api/v1/manualimport?apiKey={api_key}"
            post_data = {
                "id": entry.get("id"),
                "path": entry.get("path"),
                "artistId": entry["artist"].get("id"),
                "albumId": entry["album"].get("id"),
                "albumReleaseId": entry.get("albumReleaseId"),
                "trackIds": [track.get("id") for track in entry.get("tracks", [])],
                "quality": entry.get("quality"),
                "releaseGroup": "SpotDL",
                "additionalFile": entry.get("additionalFile"),
                "replaceExistingFiles": entry.get("replaceExistingFiles"),
                "disableReleaseSwitching": entry.get("disableReleaseSwitching"),
            }
            response_post = requests.post(post_url, json=post_data)

            if response_post.status_code == 200:
                print(f"Successfully imported: {entry['path']}")
            else:
                print(f"Error importing {entry['path']}: {response_post.status_code} {response_post.text}")

def read_input_queue():
    input_queue_file = "/app/input_queue.txt"
    if not os.path.exists(input_queue_file):
        print("No input queue file found. Exiting.")
        return []

    with open(input_queue_file, "r") as f:
        directories = [line.strip() for line in f if line.strip()]
    
    print(f"Read {len(directories)} directories from input queue.")
    return directories

downloaded_directories = read_input_queue()
if downloaded_directories:
    import_downloaded_tracks(downloaded_directories)
else:
    print("No directories to import.")
