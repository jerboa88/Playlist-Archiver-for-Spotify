<!-- Project Header -->
<div align="center">
  <img class="projectLogo" src="logo.svg" alt="Project logo" title="Project logo" width="256">

  <h1 class="projectName">Playlist Archiver for Spotify</h1>

  <p class="projectBadges">
    <img src="https://img.shields.io/badge/type-CLI_App-f44336.svg" alt="Project type" title="Project type">
    <img src="https://img.shields.io/github/languages/top/jerboa88/Playlist-Archiver-for-Spotify.svg" alt="Language" title="Language">
    <img src="https://img.shields.io/github/actions/workflow/status/jerboa88/Playlist-Archiver-for-Spotify/archive-discover-weekly.yml?logo=spotify&label=Archive%20Discover%20Weekly" alt="GitHub Workflow Status" title="GitHub Workflow Status">
    <img src="https://img.shields.io/github/actions/workflow/status/jerboa88/Playlist-Archiver-for-Spotify/archive-release-radar.yml?logo=spotify&label=Archive%20Release%20Radar" alt="GitHub Workflow Status" title="GitHub Workflow Status">
    <img src="https://img.shields.io/github/repo-size/jerboa88/Playlist-Archiver-for-Spotify.svg" alt="Repository size" title="Repository size">
    <a href="LICENSE">
      <img src="https://img.shields.io/github/license/jerboa88/Playlist-Archiver-for-Spotify.svg" alt="Project license" title="Project license"/>
    </a>
  </p>

  <p class="projectDesc">
    A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week via Github Actions, Cron, Windows Task Scheduler, or similar tools.
  </p>

  <br/>
</div>


## About
This project includes a Python script that copies and renames a playlist, as well as Github Actions workflows that can be used to automate the archival of playlists on a schedule. This script is designed to be used with Github Actions, but can be used with other automation tools as well.


## Installation
If running locally, make sure you are using Python 3, then install the required Python packages with `pip install -r requirements.txt`.


## Usage
### With Github Actions
1. Create a new app via the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard). Make sure the `Redirect URI` matches what is in the `playlist-archiver` script (ex. http://127.0.0.1:9090). Make note of the `Client ID` and `Client Secret` for later.
2. Fork this repo and clone it
3. Run the script locally to grant the script access to your Spotify account like so: `python playlist-archiver.py "input_name" "output_name" "spotify_client_id" "spotify_client_secret"`. Replace `spotify_client_id` and `spotify_client_secret` with your own values. `input_name` and `output_name` are not important at this step. After granting the app access, a `tokens.txt` file will be created in the same directory as the script. This file contains your access and refresh tokens and should be kept secret.
4. Create four repository secrets in your forked repo with the following names and values (see [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)):
    - `SPOTIFY_CLIENT_ID`: The client id from step 1
    - `SPOTIFY_CLIENT_SECRET`: The client secret from step 1
    - `SPOTIFY_ACCESS_TOKEN`: The access token from `tokens.txt`
    - `SPOTIFY_REFRESH_TOKEN`: The refresh token from `tokens.txt`
5. Create your own workflows or edit the existing ones under [.github/workflows/](.github/workflows/). The existing workflows are set up to archive Discover Weekly and Release Radar playlists every Monday and Friday, respectively. Edit the `cron` schedule to change when the script runs. See below for all available arguments for the script.

**All available arguments:**
```
usage: Playlist Archiver for Spotify [-h] [--access_token ACCESS_TOKEN] [--refresh_token REFRESH_TOKEN] [--debug] input_playlist_name output_playlist_name client_id client_secret

A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week.

positional arguments:
  input_playlist_name   The name of the playlist you want to make a copy of. The name must match exactly. This is required
  output_playlist_name  The name of the output playlist. strftime format codes can be used to include the date/time in the name. This is required
  client_id             Your client ID for Spotify. A client ID is required for this program to work
  client_secret         Your client secret for Spotify. A client secret is required for this program to work

options:
  -h, --help            show this help message and exit
  --access_token ACCESS_TOKEN, -a ACCESS_TOKEN
                        Your access token for Spotify. This can be found in tokens.txt after the program is run for the first time
  --refresh_token REFRESH_TOKEN, -r REFRESH_TOKEN
                        Your refresh token for Spotify. This can be found in tokens.txt after the program is run for the first time
  --debug, -d           Whether to print additional information to the console for debugging. Default: false
```


## Limitations
- This script must be run once locally before the Github Actions workflows will work. This is because the Spotify API requires user authorization via the browser, which is not possible in a headless environment
- Playlists can not be placed into folders because there is currently no way to create or manage folders via the Spotify API. If you want the archived playlist to be in a folder, you will have to move them manually


## Contributing
Contributions, issues, and forks are welcome but this is a hobby project so don't expect too much from it. [SemVer](http://semver.org/) is used for versioning.


## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

This project includes various resources which carry their own copyright notices and license terms. See LICENSE-THIRD-PARTY.md for more details.
