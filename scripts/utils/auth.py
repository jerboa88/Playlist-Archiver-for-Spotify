import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils.logging import get_logger


logger = get_logger()


# Authorize with the Spotify API
def authorize(scope, client_id, client_secret, redirect_uri, cache_handler, open_browser=False):
	logger.debug('Connecting to the Spotify API')

	return spotipy.Spotify(auth_manager=SpotifyOAuth(
		scope=scope,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		cache_handler=cache_handler,
		open_browser=open_browser,
	))
