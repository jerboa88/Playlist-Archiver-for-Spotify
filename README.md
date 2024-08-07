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

  <p class="projectDesc" data-exposition="A CLI app that automatically archives Spotify playlists. Written in Python, this program is designed to be run as part of a scheduled CI workflow using GitHub Actions. This project was created as a way to automate a task I was doing manually, and to get more experience working with GitHub Actions and the Spotify API.">
    Automatically archive Spotify playlists using Python & GitHub Actions. Never lose your Discover Weekly playlist again!
  </p>

  <br/>
</div>


## About
A Python script for copying Spotify playlists. This can be used with the provided GitHub Actions workflows to automatically archive Discover Weekly and Release Radar playlists every week.

If you prefer, you can run the script manually, or with other automation tools like Cron or Windows Task Scheduler instead of GitHub Actions.


## Installation
If running locally, make sure you are using Python 3, then install the required Python packages with `pip install -r requirements.txt`.


## Usage
### With GitHub Actions

> [!NOTE]
> GitHub automatically disables scheduled workflows if there has been no repository activity for some time. When a workflow is about to be disabled, GitHub will send you an email and give you the option to keep running it in the `Actions` tab. Alternatively, you can make a commit every 60 days to keep the repository active.

1. Create a new app via the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard). Make sure the `Redirect URI` you set matches what is in `common.py` (it is `http://127.0.0.1:9090` by default). Make note of the `Client ID` and `Client Secret` for later.
2. Fork this repo and clone it
3. Run `python setup.py SPOTIFY_CLIENT_ID SPOTIFY_CLIENT_SECRET` on your local machine to grant the script access to your Spotify account. Replace `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` with your own values from step 1. After granting the app access, a `tokens.txt` file will be created in the same directory as the script. This file contains your access and refresh tokens and should be kept secret.
4. Create four repository secrets in your forked repo with the following names and values (see [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)):
    - `SPOTIFY_CLIENT_ID`: The client id from step 1
    - `SPOTIFY_CLIENT_SECRET`: The client secret from step 1
    - `SPOTIFY_ACCESS_TOKEN`: The access token from step 3
    - `SPOTIFY_REFRESH_TOKEN`: The refresh token from step 3
5. Create your own workflows or edit the existing ones under [.github/workflows/](.github/workflows/). The existing workflows are set up to archive Discover Weekly and Release Radar playlists every Monday and Friday, respectively. Edit the `cron` schedule to change when the script runs. See below for all available arguments for the script.

**Script usage:**
```
usage: Playlist Archiver for Spotify [-h] [--debug] client_id client_secret access_token refresh_token input_playlist_name output_playlist_name

A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week.

positional arguments:
  client_id             Your client ID for Spotify. A client ID is required for this program to work
  client_secret         Your client secret for Spotify. A client secret is required for this program to work
  access_token          Your access token for Spotify. This can be found in tokens.txt after the program is run for the first time
  refresh_token         Your refresh token for Spotify. This can be found in tokens.txt after the program is run for the first time
  input_playlist_name   The name of the playlist you want to make a copy of. The name must match exactly. This is required
  output_playlist_name  The name of the output playlist. strftime format codes can be used to include the date/time in the name. This is required

options:
  -h, --help            show this help message and exit
  --debug, -d           Whether to print additional information to the console for debugging. Default: false
```


## Limitations
- The setup script must be run once locally before the GitHub Actions workflows will work. This is because the Spotify API requires user authorization via the browser, which is not possible in a headless environment
- Playlists can not be placed into folders because there is currently no way to create or manage folders via the Spotify API. If you want the archived playlist to be in a folder, you will have to move them manually


## Contributing
Contributions, issues, and forks are welcome but this is a hobby project so don't expect too much from it. [SemVer](http://semver.org/) is used for versioning.


## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

This project includes various resources which carry their own copyright notices and license terms. See [LICENSE-THIRD-PARTY.md](LICENSE-THIRD-PARTY.md) for more details.
