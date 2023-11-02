# Reusable classes and functions
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler


# Constants
CONSTANTS = {
	'app_name': 'Playlist Archiver for Spotify',
	'app_desc': 'A Python script that makes a copy of a playlist. Useful for automating archival of Discover Weekly and Release Radar playlists every week.',
	'scope': 'playlist-read-private playlist-read-collaborative playlist-modify-private',
	'redirect_uri': 'http://127.0.0.1:9090',
	'tokens_filename': 'tokens.txt',
}


# Logging functions
def debug(msg, is_debug_mode=False):
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


# Spotify authorization
def authorize(scope, client_id, client_secret, redirect_uri, cache_handler, open_browser=False):
	debug('Connecting to the Spotify API')

	return spotipy.Spotify(auth_manager=SpotifyOAuth(
		scope=scope,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		cache_handler=cache_handler,
		open_browser=open_browser,
	))
