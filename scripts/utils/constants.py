# Constants
APP_NAME = 'Playlist Archiver for Spotify'
APP_URL = 'https://johng.io/p/playlist-archiver-for-spotify'
SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
REDIRECT_URI = 'http://127.0.0.1:9090'
TOKENS_FILENAME = 'tokens.yaml'
SAVED_TRACKS_KEYWORD = 'saved_tracks'
ARG_DESCS = {
	'client_id': 'Your client ID for Spotify. Get one from https://developer.spotify.com/dashboard',
	'client_secret': 'Your client secret for Spotify. Get one from https://developer.spotify.com/dashboard',
	'access_token': f'Your access token for Spotify. This can be found in {TOKENS_FILENAME} after the program is run for the first time',
	'refresh_token': f'Your refresh token for Spotify. This can be found in {TOKENS_FILENAME} after the program is run for the first time',
	'playlist_names': 'A list of playlist names you want to find the ID for. If multiple names are entered, we will try to match them to playlists in the order they are given. One of the names must match exactly',
	'input_playlist_id': "The ID of the playlist you want to make a copy of, or the special string 'saved_tracks' to make a copy of your 'Liked Songs' playlist",
	'output_playlist_name': 'The name of the output playlist. strftime format codes can be used to include the date/time in the name',
	'--visibility': "Set the visibility of the output playlist. When set to 'auto', the visibility will be set to that of the input playlist (default: auto)",
	'--contributions': "Set the contribution mode of the output playlist. When set to 'auto', the contribution mode will be set to that of the input playlist (default: auto)",
	'debug': 'Whether to print additional information to the console for debugging (default: false)',
}
