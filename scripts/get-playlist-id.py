import argparse
from utils.constants import ARG_DESCS, SCOPE, REDIRECT_URI
from utils.logging import get_logger, enable_debug_logging
from utils.auth import authorize
from utils.cache import CacheArgHandler
from utils.validation import assert_valid_client_id, assert_valid_client_secret, assert_valid_access_token, assert_valid_refresh_token, assert_valid_playlist_names


SCRIPT_NAME = 'get-playlist-id.py'
SCRIPT_DESC = 'Get the ID of a Spotify playlist given a list of names.'


logger = get_logger()


# Parse command line arguments
def parse_args():
	logger.debug('Parsing arguments')

	parser = argparse.ArgumentParser(prog=SCRIPT_NAME, description=SCRIPT_DESC)

	parser.add_argument('client_id', help=ARG_DESCS['client_id'])
	parser.add_argument('client_secret', help=ARG_DESCS['client_secret'])
	parser.add_argument('access_token', help=ARG_DESCS['access_token'])
	parser.add_argument('refresh_token', help=ARG_DESCS['refresh_token'])
	parser.add_argument('playlist_names', help=ARG_DESCS['playlist_names'], nargs='+')
	parser.add_argument('--debug', '-d', help=ARG_DESCS['debug'], default=False, action='store_true')

	args = parser.parse_args()

	if args.debug:
		enable_debug_logging(logger)

	assert_valid_client_id(args.client_id)
	assert_valid_client_secret(args.client_secret)
	assert_valid_access_token(args.access_token)
	assert_valid_refresh_token(args.refresh_token)
	assert_valid_playlist_names(args.playlist_names)

	return args


# Try to match a list of playlist names to a playlist
def does_playlist_match_names(sp, playlist_name, playlist_names):
	for name in playlist_names:
		if name == playlist_name:
			logger.debug(f'Found playlist "{name}"')

			return True

	return False


# Get the ID of a playlist given its name
def get_playlist_id(sp, playlist_names):
	logger.debug(f'Searching for playlists with names {playlist_names}')

	chunk_size = 50
	chunk_offset = 0
	playlist_id = None
	available_playlist_names = []

	while not playlist_id:
		chunked_playlists = sp.current_user_playlists(limit=chunk_size, offset=chunk_offset)['items']

		if not chunked_playlists:
			break

		for playlist in chunked_playlists:
			if does_playlist_match_names(sp, playlist['name'], playlist_names):
				playlist_id = playlist['id']

				logger.debug(f'Playlist has ID {playlist_id}')

				break
			else:
				available_playlist_names.append(playlist['name'])

		chunk_offset += chunk_size

	if not playlist_id:
		available_playlist_names.sort()

		formatted_available_playlist_names = '\n  '.join(available_playlist_names)

		logger.debug(f'Finished searching through playlists:\n  {formatted_available_playlist_names}')

		raise ValueError(f'Playlist {playlist_names} not found. Is the playlist name correct?')

	return playlist_id


# Script entry point
def main():
	logger.debug('Script started')

	args = parse_args()
	cache_handler = CacheArgHandler(SCOPE, args.access_token, args.refresh_token)
	sp = authorize(SCOPE, args.client_id, args.client_secret, REDIRECT_URI, cache_handler)
	user_id = sp.me()['id']
	playlist_id = get_playlist_id(sp, args.playlist_names)

	print(playlist_id)

	logger.debug('Script finished')


main()