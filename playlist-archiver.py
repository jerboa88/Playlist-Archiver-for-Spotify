import argparse, json, os, spotipy
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth


# Constants
app_name = 'Playlist Archiver for Spotify'
app_desc = 'A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week.'
scope = ['playlist-read-private', 'playlist-read-collaborative', 'playlist-modify-private']
client_secret_filename = 'client_secret.txt'
redirect_uri = 'http://127.0.0.1:9090'
is_debug_mode = False


# Functions
def debug(msg):
	if is_debug_mode:
		print(f'DEBUG: {msg}')


def warn(msg):
	print(f'WARN: {msg}')


def parse_args(app_name, app_desc):
	debug('Parsing arguments')

	descriptions = {
		'input_playlist_name': 'The name of the playlist you want to make a copy of. The name must match exactly. This is required',
		'output_playlist_name': 'The name of the output playlist. strftime format codes can be used to include the date/time in the name. This is required',
		'client_id':
		'Your client ID for Spotify. A client ID is required for this program to work',
		'client_secret': f'Your Client Secret for Spotify. It is recommended to put this in {client_secret_filename} instead of passing it as an argument. A client secret is required for this program to work',
		'debug': 'Whether to print additional information to the console for debugging. Default: false'
	}
	parser = argparse.ArgumentParser(prog=app_name, description=app_desc)

	parser.add_argument('input_playlist_name', help=descriptions['input_playlist_name'])
	parser.add_argument('output_playlist_name', help=descriptions['output_playlist_name'])
	parser.add_argument('client_id', help=descriptions['client_id'])
	parser.add_argument('--client_secret', '-s', help=descriptions['client_secret'])
	parser.add_argument('--debug', '-d', help=descriptions['debug'], default=False, action='store_true')
	args = parser.parse_args()

	# Check input playlist name
	if not args.input_playlist_name:
		raise ValueError('The input playlist name cannot be empty')

	# Check output playlist name
	if not args.output_playlist_name:
		raise ValueError('The output playlist name cannot be empty')

	# Check client ID
	if args.client_id:
		if len(args.client_id) != 32:
			raise ValueError('The entered client ID is invalid. It must be 32 characters long')

	# Check client secret
	if args.client_secret:
		if len(args.client_secret) != 32:
			raise ValueError('The entered client secret is invalid. It must be 32 characters long')

	else:
		if os.path.exists(client_secret_filename):
			try:
				args.client_secret = open(client_secret_filename, 'r').read(32)

			except OSError:
				raise Exception(f'{client_secret_filename} could not be read')

		else:
			raise Exception(
				f'{client_secret_filename} does not exist. Please put your Spotify client secret in {client_secret_filename} or pass it as a command line argument')

	return args


def authorize(scope, client_id, client_secret, redirect_uri):
	debug('Connecting to the Spotify API')

	return spotipy.Spotify(auth_manager=SpotifyOAuth(
		scope=scope,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri
	))


def get_playlist_id(playlist_name):
	debug(f'Getting playlist id for {playlist_name}')

	chunk_size = 50
	chunk_offset = 0
	playlist_id = None

	while not playlist_id:
		chunked_playlists = sp.current_user_playlists(limit=chunk_size, offset=chunk_offset)['items']

		if not chunked_playlists:
			debug('Finished searching through playlists')
			break

		for playlist in chunked_playlists:
			if playlist['name'] == playlist_name:
				playlist_id = playlist['id']
				debug(f'Playlist id of {playlist_name} is {playlist_id}')

		chunk_offset += chunk_size

	if not playlist_id:
		warn(f'Playlist {playlist_name} not found. Is the playlist name correct?')

	return playlist_id


def get_playlist_track_ids(playlist_id):
	debug(f'Getting track ids for playlist {playlist_id}')

	chunk_size = 100
	chunk_offset = 0
	track_ids = []

	while True:
		chunked_tracks = sp.playlist_tracks(playlist_id, fields='items(track(id))', limit=chunk_size, offset=chunk_offset)['items']

		if not chunked_tracks:
			debug(f'{len(track_ids)} track ids found')
			break

		track_ids.extend(list(map(lambda track : track['track']['id'], chunked_tracks)))

		chunk_offset += chunk_size

	return track_ids


def create_playlist(user_id, playlist_name, track_ids, app_name):
	debug(f'Creating new playlist {playlist_name}')

	ts = datetime.now()
	playlist_name = ts.strftime(playlist_name)
	playlist = sp.user_playlist_create(user_id, playlist_name, public=False, collaborative=False, description=f'Playlist created by {app_name} on {ts}')

	sp.playlist_add_items(playlist['id'], track_ids)

	debug(f'Playlist created: {playlist}')


print('Script started')

args = parse_args(app_name, app_desc)
is_debug_mode = args.debug

print(is_debug_mode)

sp = authorize(scope, args.client_id, args.client_secret, redirect_uri)
user_id = sp.me()['id']
playlist_id = get_playlist_id(args.input_playlist_name)
track_ids = get_playlist_track_ids(playlist_id)
create_playlist(user_id, args.output_playlist_name, track_ids, app_name)

print('Script finished')