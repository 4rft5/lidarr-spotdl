# lidarr-spotdl
spotDL integration for Lidarr.

## Information
Lidarr-spotDL is an integration that allows for monitored albums and tracks to be downloaded and added into Lidarr via spotDL.

<sub>This is a heavily modified (and actually working) fork of <a href="https://gitlab.com/rmnavz/lidarrspotdl">LidarrSpotDL</a>.</sub>

## Quick Start
### Needed Credentials:
  To utilize Lidarr-spotDL, you will need your Lidarr API key, as well as a <a href="https://developer.spotify.com/">Spotify Client ID and Secret.</a>

  It is highly recommended to store your API keys in .env files or a secrets manager.


### Utilizing Docker-Compose
```
services:
  lidarr-spotdl:
    container_name: spotdl-lidarr
    image: ghcr.io/4rft5/lidarr-spotdl:latest
    environment:
      - TZ=ETC/UTC # Change to your time zone
      - LIDARR_URL=http://localhost:8686 # Change to your Lidarr endpoint (either IP:Port or Hostname)
      - LIDARR_API_KEY=<your-lidarr-api-key>
      - SPOTIFY_CLIENT_ID=<your-spotify-client-id>
      - SPOTIFY_CLIENT_SECRET=<your-spotify-client-secret>
      - MINUTE_INTERVAL=30 # Interval between scans of Lidarr
    volumes:
      -  /your/media/folder:/downloads/music
    restart: unless-stopped
```

### Docker Run
If you prefer to run without Docker Compose, you can use the following `docker run` command:
```
docker run -d \
  --name ghcr.io/4rft5/lidarr-spotdl:latest \
  -e TZ=ETC/UTC \ # Change to your time zone
  -e LIDARR_URL=http://localhost:8686 \ # Change to your Lidarr endpoint  (either IP:Port or Hostname)
  -e LIDARR_API_KEY=<your-lidarr-api-key> \
  -e SPOTIFY_CLIENT_ID=<your-spotify-client-id> \
  -e SPOTIFY_CLIENT_SECRET=<your-spotify-client-secret> \
  -e MINUTE_INTERVAL=30 \ # Interval between scans of Lidarr
  -v /your/media/folder:/downloads/music \
  --restart unless-stopped \
  spotdl-lidarr
```

### Compile Yourself
Download the source code from this repo.

Build with the command `docker build -t 4rft5/lidarr-spotdl:latest .`

## How it Works
This container, when started, checks to see if there are any missing and monitored tracks or albums (their artists must also be monitored) in Lidarr, and uses the Spotify API to search for them before downloading them via SpotDL.

Music is then cataloged in the style of `/Artist/Album/(SpotDL Downloads)`, which allows it to be found by Lidarr in a library scan, given the volume path is set to your media or music folder.

The container will then run checks for new items to download via the Lidarr API at intervals set in the configuration until stopped.

## Contributions

Pull Requests and other contributions are welcome. I've never made a Docker image before, so some things may not be as streamlined as they could be.

### Issues

I attempted to test with everything I could think of, however may have missed some things that could cause the container to crash or otherwise behave abnormally. Please open an issue or pull request here for those.
