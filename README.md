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
A Python script for making copies of Spotify playlists. This can be used with the provided GitHub Actions workflows to automatically archive Discover Weekly and Release Radar playlists every week.

If you prefer, you can run the script manually, or with other automation tools like Cron or Windows Task Scheduler instead of GitHub Actions.


## Getting Started

### Prerequisites
- A Spotify account
- A GitHub account (if you want to use GitHub Actions to run the script)
- Python 3

### Installation
1. Create a new app via the [Spotify Developer Dashboard]. Make sure the `Redirect URI` you set matches what is in [constants.py] (it is `http://127.0.0.1:9090` by default). Make note of the `Client ID` and `Client Secret` for later.
2. Clone or download this repo. If you are planning to use GitHub Actions, you probably want to fork this repo first.
3. Install the required Python packages with `pip install -r requirements.txt`.
4. Run `python setup.py SPOTIFY_CLIENT_ID SPOTIFY_CLIENT_SECRET` to grant the script access to your Spotify account. Replace `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` with your own values. After granting the app access, a `tokens.yaml` file will be created in the same directory as the script. This file contains your access and refresh tokens and should be kept secret.


## Usage
To copy a playlist, you'll need to call [copy-playlist.py] with the ID of the input playlist, a name for the destination playlist, and your Spotify credentials. See [Advanced Script Usage] for more details.

To find the ID of a playlist, see [Finding the Playlist ID].

For examples on how to run the script automatically, see [Scheduling].

### Finding the Playlist ID
#### Manually
If you already know the playlist you want to copy, the most reliable way to get its ID is to just copy it from Spotify.

1. Open Spotify and navigate to the playlist you want to copy.
2. Right-click on the playlist and select `Share` > `Copy link to playlist`.
3. The ID of the playlist is the last part of the URL. For example, the ID of the playlist `https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC` is `37i9dQZF1DXdPec7aLTmlC`.

#### Programmatically
> [!IMPORTANT]
> This helper script may not work reliably because the Spotify API no longer seems to return curated playlists like Discover Weekly and Release Radar in the list of a user's playlists. Feel free to try it, but if you want to copy these playlists, you'll probably need to use the manual method instead.

If you want to programmatically find the ID of a playlist, you can use the [get-playlist-id.py] helper script. This script will search for a playlist with a given name and return its ID. See [Advanced Script Usage] for more details.


### Scheduling
#### With GitHub Actions
We can use GitHub Actions to automatically run the script every week.

> [!NOTE]
> GitHub automatically disables scheduled workflows if there has been no repository activity for some time. When a workflow is about to be disabled, GitHub will send you an email and give you the option to keep running it in the `Actions` tab. Alternatively, you can make a commit every 60 days to keep the repository active.

1. Create four repository secrets in your forked repo with the following names and values (see [Using secrets in GitHub Actions]):
    - `SPOTIFY_CLIENT_ID`: The client id from step 1
    - `SPOTIFY_CLIENT_SECRET`: The client secret from step 1
    - `SPOTIFY_ACCESS_TOKEN`: The access token from step 4
    - `SPOTIFY_REFRESH_TOKEN`: The refresh token from step 4
2. Create your own workflows or edit the existing ones under [.github/workflows/]. The existing workflows are set up to archive Discover Weekly and Release Radar playlists every Monday and Friday, respectively. Edit the `cron` schedule to change when the script runs. See below for all available arguments for the script.


### Advanced Script Usage

> [!WARNING]
> When debug mode is enabled, these scripts may print potentially private information from your Spotify account to the console like playlist IDs and names. This is useful for debugging, but if your workflow logs are public and you don't want to share this information, consider disabling debug logging.

#### [setup.py]
This script is used to grant access to your Spotify account and save the access and refresh tokens to a file for later use.

This script can't be run in a headless environment because a browser window needs to be opened to prompt you to grant access to the script. Instead, run this script on your local machine and save the tokens as repository secrets or environment variables on your server.

```
usage: setup.py [-h] [--debug] client_id client_secret

Grant access to your Spotify account and save the access and refresh tokens to a file.

positional arguments:
  client_id      Your client ID for Spotify. Get one from https://developer.spotify.com/dashboard
  client_secret  Your client secret for Spotify. Get one from https://developer.spotify.com/dashboard

options:
  -h, --help     show this help message and exit
  --debug, -d    Whether to print additional information to the console for debugging. Default: false
```

#### [get-playlist-id.py]
If you don't know the ID of a playlist, you can use this helper script to find it. Pass in a list of 1 or more playlist names and it will print the ID of the first playlist that matches.

You can either use this script as as standalone tool, or you can use the output of this script directly in [copy-playlist.py] as part of your workflow.

```
usage: get-playlist-id.py [-h] [--debug] client_id client_secret access_token refresh_token playlist_names [playlist_names ...]

Get the ID of a Spotify playlist given a list of names.

positional arguments:
  client_id       Your client ID for Spotify. Get one from https://developer.spotify.com/dashboard
  client_secret   Your client secret for Spotify. Get one from https://developer.spotify.com/dashboard
  access_token    Your access token for Spotify. This can be found in tokens.yaml after the program is run for the first time
  refresh_token   Your refresh token for Spotify. This can be found in tokens.yaml after the program is run for the first time
  playlist_names  A list of playlist names you want to find the ID for. If multiple names are entered, we will try to match them to playlists in the order
                  they are given. One of the names must match exactly

options:
  -h, --help      show this help message and exit
  --debug, -d     Whether to print additional information to the console for debugging. Default: false
```

#### [copy-playlist.py]
This is the main script that copies a playlist. It takes in the ID of the input playlist and the name of the output playlists, and copies all the tracks from the input playlist to the output playlist. If the output playlist does not exist, it will be created.

You can include [strftime format codes] in the output playlist name to include the date/time in the name. For example, `Discover Weekly - %Y-%m-%d` will create a new playlist with the name `Discover Weekly - 2025-01-01`.

```
usage: copy-playlist.py [-h] [--debug] client_id client_secret access_token refresh_token input_playlist_id output_playlist_name

Make a copy of a given playlist.

positional arguments:
  client_id             Your client ID for Spotify. Get one from https://developer.spotify.com/dashboard
  client_secret         Your client secret for Spotify. Get one from https://developer.spotify.com/dashboard
  access_token          Your access token for Spotify. This can be found in tokens.yaml after the program is run for the first time
  refresh_token         Your refresh token for Spotify. This can be found in tokens.yaml after the program is run for the first time
  input_playlist_id     The ID of the playlist you want to make a copy of
  output_playlist_name  The name of the output playlist. strftime format codes can be used to include the date/time in the name

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


[Finding the Playlist ID]: #finding-the-playlist-id
[Scheduling]: #scheduling
[Advanced Script Usage]: #advanced-script-usage
[setup.py]: scripts/setup.py
[get-playlist-id.py]: scripts/get-playlist-id.py
[copy-playlist.py]: scripts/copy-playlist.py
[constants.py]: scripts/utils/constants.py
[.github/workflows/]: .github/workflows/
[Spotify Developer Dashboard]: https://developer.spotify.com/dashboard
[Using secrets in GitHub Actions]: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
[strftime format codes]: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
