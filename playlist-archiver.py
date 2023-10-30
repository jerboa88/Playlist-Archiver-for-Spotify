import argparse, spotipy
from datetime import datetime
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth


# Constants
app_name = 'Playlist Archiver for Spotify'
app_desc = 'A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week.'
scope = 'playlist-read-private playlist-read-collaborative playlist-modify-private'
tokens_filename = 'tokens.txt'
tokens_save_msg = f'Please create Github secrets for both of these tokens. Do not push this file to Github'
redirect_uri = 'http://127.0.0.1:9090'
is_debug_mode = False


# Helper functions
def debug(msg):
	if is_debug_mode:
		print(f'DEBUG: {msg}')


def warn(msg):
	print(f'WARN: {msg}')


# Custom cache handler for Spotipy
class CacheArgHandler(CacheHandler):
	"""
	A cache handler that stores the token info in memory as an
	instance attribute of this class. The token info will be lost when this
	instance is freed. Token info can also be passed in as arguments to the
	constructor if they have been cached elsewhere.
	"""

	def __init__(self, scope=None, access_token=None, refresh_token=None, token_type='Bearer', expires_in=3600, expires_at=0):
		self.scope = scope
		self.access_token = access_token
		self.refresh_token = refresh_token
		self.token_type = token_type
		self.expires_in = expires_in
		self.expires_at = expires_at


	def get_cached_token(self):
		if not self.access_token or not self.refresh_token:
			return None

		return {
				'scope': self.scope,
				'access_token': self.access_token,
				'refresh_token': self.refresh_token,
				'token_type': self.token_type,
				'expires_in': self.expires_in,
				'expires_at': self.expires_at,
		}


	def save_token_to_cache(self, token_info):
		self.scope = token_info['scope']
		self.access_token = token_info['access_token']
		self.refresh_token = token_info['refresh_token']
		self.token_type = token_info['token_type']
		self.expires_in = token_info['expires_in']
		self.expires_at = token_info['expires_at']


	def save_token_to_file(self):
		try:
			f = open(tokens_filename, 'w')
			f.write(f'# {tokens_save_msg}\nSPOTIFY_ACCESS_TOKEN: {self.access_token}\nSPOTIFY_REFRESH_TOKEN: {self.refresh_token}')
			f.close()
		except IOError:
			warn(f'Couldn\'t write tokens to cache to: {tokens_filename}')

		print(f'Tokens were saved to {tokens_filename}. {tokens_save_msg}')


# Functions
def parse_args(app_name, app_desc):
	debug('Parsing arguments')

	descriptions = {
		'input_playlist_name': 'The name of the playlist you want to make a copy of. The name must match exactly. This is required',
		'output_playlist_name': 'The name of the output playlist. strftime format codes can be used to include the date/time in the name. This is required',
		'client_id': 'Your client ID for Spotify. A client ID is required for this program to work',
		'client_secret': f'Your client secret for Spotify. A client secret is required for this program to work',
		'access_token': f'Your access token for Spotify. This can be found in {tokens_filename} after the program is run for the first time',
		'refresh_token': f'Your refresh token for Spotify. This can be found in {tokens_filename} after the program is run for the first time',
		'debug': 'Whether to print additional information to the console for debugging. Default: false'
	}
	parser = argparse.ArgumentParser(prog=app_name, description=app_desc)

	parser.add_argument('input_playlist_name', help=descriptions['input_playlist_name'])
	parser.add_argument('output_playlist_name', help=descriptions['output_playlist_name'])
	parser.add_argument('client_id', help=descriptions['client_id'])
	parser.add_argument('client_secret', help=descriptions['client_secret'])
	parser.add_argument('--access_token', '-a', help=descriptions['access_token'])
	parser.add_argument('--refresh_token', '-r', help=descriptions['refresh_token'])
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

	return args


def authorize(scope, client_id, client_secret, redirect_uri, cache_handler):
	debug('Connecting to the Spotify API')

	return spotipy.Spotify(auth_manager=SpotifyOAuth(
		scope=scope,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		cache_handler=cache_handler
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
cache_handler = CacheArgHandler(scope, args.access_token, args.refresh_token)


if args.access_token and args.refresh_token:
	sp = authorize(scope, args.client_id, args.client_secret, redirect_uri, cache_handler)
	user_id = sp.me()['id']
	playlist_id = get_playlist_id(args.input_playlist_name)
	track_ids = get_playlist_track_ids(playlist_id)
	create_playlist(user_id, args.output_playlist_name, track_ids, app_name)
else:
	print('Access token and refresh token not provided. Opening browser to authorize with Spotify')
	sp = authorize(scope, args.client_id, args.client_secret, redirect_uri, cache_handler)
	user_id = sp.me()['id']
	cache_handler.save_token_to_file()

print('Script finished')
