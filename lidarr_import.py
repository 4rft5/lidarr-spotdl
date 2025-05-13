import os
import requests
from pyarr import LidarrAPI
import json

def import_downloaded_tracks(downloaded_directories):
    lidarr = LidarrAPI(
        os.getenv("LIDARR_URL", "http://your-lidarr-ip:port"),
        os.getenv("LIDARR_API_KEY", "your-lidarr-api-key")
    )

    try:
        missing = lidarr.get_wanted(missing=True).get("records", [])
        print(f"Retrieved {len(missing)} missing albums from Lidarr")
    except Exception as e:
        print(f"Failed to fetch missing albums: {e}")
        return
    index = {}
    for r in missing:
        art = r["artist"]["artistName"]
        alb = r["title"]
        index.setdefault(art.lower(), {})[alb.lower()] = r
    for full_path in downloaded_directories:
        print(f"\nChecking path: {full_path}")
        
        parts = full_path.rstrip("/").split("/")
        if len(parts) < 3:
            print("  Invalid path, skipping")
            continue
        artist_name = parts[-2]
        album_title = parts[-1]
        print(f"  Artist: {artist_name!r}, Album: {album_title!r}")

        rec = index.get(artist_name.lower(), {}).get(album_title.lower())
        if not rec:
            print("  No matching missing-album record found, skipping")
            continue

        album_id = rec['id']
        print(f"  Matched record (ID={album_id}), scanning folder...")

        try:
            tracks = lidarr.get_tracks(albumId=album_id)
            track_ids = [track['id'] for track in tracks]
            print(f"  Found {len(track_ids)} tracks for the album.")
        except Exception as e:
            print(f"  Error fetching tracks for album {album_title}: {e}")
            continue

        track_files = [
            os.path.join(full_path, f) for f in os.listdir(full_path)
            if os.path.isfile(os.path.join(full_path, f))
        ]

        if not track_files:
            print("  No files found in directory.")
            continue

        for track_file in track_files:
            print(f"  🛠️ Attempting manual import for file: {track_file}...")
            
            manual_import_payload = [{
                "path": track_file,
                "albumId": album_id,
                "trackIds": track_ids,
                "replaceExistingFiles": True
            }]
            
            try:
                headers = {
                    "X-Api-Key": os.getenv("LIDARR_API_KEY", "your-lidarr-api-key"),
                    "Content-Type": "application/json"
                }
                lidarr_url = os.getenv("LIDARR_URL", "http://your-lidarr-ip:port")
                response = requests.post(f"{lidarr_url}/api/v1/manualimport", json=manual_import_payload, headers=headers)

                if response.status_code == 202:
                    print(f"  Successfully accepted import request for file: {track_file}")
                    with open("import_response.json", "w") as f:
                        json.dump(response.json(), f, indent=4)
                    print("  Response saved to 'import_response.json'.")
                else:
                    print(f"  Failed to import file {track_file}, status code: {response.status_code}, message: {response.text}")

            except Exception as e:
                print(f"  Error during manual import of file {track_file}: {e}")

def read_input_queue():
    fn = "/app/input_queue.txt"
    if not os.path.exists(fn):
        print("No input queue file found.")
        return []
    with open(fn) as f:
        dirs = [l.strip() for l in f if l.strip()]
    print(f"Found {len(dirs)} paths in input queue")
    return dirs

if __name__ == "__main__":
    downloaded = read_input_queue()
    if downloaded:
        import_downloaded_tracks(downloaded)
    else:
        print("Nothing to import.")
