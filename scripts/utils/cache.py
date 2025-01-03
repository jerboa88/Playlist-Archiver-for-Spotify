from spotipy.cache_handler import CacheHandler


# Custom cache handler for Spotipy
class CacheArgHandler(CacheHandler):
	"""
	A cache handler that stores the token info in memory as an
	instance attribute of this class. The token info will be lost when this
	instance is freed. Token info can also be passed in as arguments to the
	constructor if they have been cached elsewhere.
	"""

	def __init__(
		self,
		scope=None,
		access_token=None,
		refresh_token=None,
		token_type='Bearer',
		expires_in=3600,
		expires_at=0,
	):
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
