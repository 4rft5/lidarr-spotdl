import os
import requests
import argparse
import subprocess
import json
import shutil
import spotipy
import re
import logging
from spotipy.oauth2 import SpotifyClientCredentials

log_file_path = "/logs/run_spotdl.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO)

def sanitize_directory_name(name):
    sanitized_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    return sanitized_name

def search_spotify(artist_url, song_name, album_name=None):
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "your-client-id")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "your-client-secret")

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    artist_id = artist_url.split(':')[-1]

    basic_query = f'artist:{artist_id}'

    if album_name:
        basic_query += f' album:{album_name}'
    else:
        basic_query += f' track:{song_name}'

    # print(f"Spotipy Query: {basic_query}")
    

    if album_name:
        results = sp.search(q=basic_query, type='album', limit=1)
        if results['albums']['items']:
            album_url = results['albums']['items'][0]['external_urls']['spotify']
            print (" ")
            print(f"Download completed for '{album_name}' by {artist_id}.")
            return album_url
        else:
            print(f"No results found for '{song_name}' by {artist_id} on Spotify.")
            return None
    else:
        results = sp.search(q=basic_query, type='track', limit=1)
        if results['tracks']['items']:
            track_url = results['tracks']['items'][0]['external_urls']['spotify']
            print(" ")
            print(f"Download completed for '{song_name}' by {artist_id}.")
            return track_url
        else:
            print(f"No direct track match for '{song_name}' by {artist_id} on Spotify.")
            return None

def extract_spotify_urls_and_download(download_dir):
    lidarr_url = os.getenv("LIDARR_URL", "http://your-lidarr-ip:port")
    api_key = os.getenv("LIDARR_API_KEY", "your-lidarr-api-key")
    endpoint = f"{lidarr_url}/api/v1/wanted/missing?apiKey={api_key}"

    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: Received status code {response.status_code} from Lidarr API")
        print(response.text)
        return 

    downloaded_directories = []

    for record in data.get("records", []):
        artist_links = record.get("artist", {}).get("links", [])

        for link in artist_links:
            if link.get("name") == "spotify":
                spotify_artist_url = link.get("url")

                monitored_release = None
                for release in record.get("releases", []):
                    if release.get("monitored", False):
                        monitored_release = release
                        break
                
                if monitored_release:
                    album_name = record.get("title", monitored_release.get("title", "Unknown Album"))

                    sanitized_artist_name = sanitize_directory_name(record['artist']['artistName'])

                    if album_name == "Unknown Album":
                        track_url = search_spotify(record['artist']['artistName'], record['title'])
                    else:
                        track_url = search_spotify(record['artist']['artistName'], record['title'], album_name)
                    
                    if track_url:
                        sanitized_artist_name = sanitize_directory_name(record['artist']['artistName'])
                        album_folder = f"{download_dir}/{sanitized_artist_name}/{sanitize_directory_name(album_name)}"
                        os.makedirs(album_folder, exist_ok=True)

                        download_command = f"spotdl \"{track_url}\" --output \"{album_folder}\""
                        subprocess.run(download_command, shell=True, check=True)
                        downloaded_directory = f"{album_folder}"
                        downloaded_directories.append(downloaded_directory)         

    logging.info(f"Downloaded directories: {downloaded_directories}")
    if not downloaded_directories:
        print("No new tracks or albums found to download.")
        print(" ")
    else:
        print(json.dumps(downloaded_directories))


parser = argparse.ArgumentParser(description='Extract Spotify URLs and download with SpotDL')
parser.add_argument('--download-dir', type=str, default='/downloads/music', help='Download directory')
args = parser.parse_args()

extract_spotify_urls_and_download(args.download_dir)

