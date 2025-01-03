import argparse
from datetime import datetime
from utils.constants import APP_NAME, APP_URL, ARG_DESCS, SCOPE, REDIRECT_URI
from utils.logging import get_logger, enable_debug_logging
from utils.auth import authorize
from utils.cache import CacheArgHandler
from utils.validation import (
	assert_valid_client_id,
	assert_valid_client_secret,
	assert_valid_access_token,
	assert_valid_refresh_token,
	assert_valid_input_playlist_id,
	assert_valid_output_playlist_name,
)


# Constants
__SCRIPT_NAME = 'copy-playlist.py'
__SCRIPT_DESC = 'Make a copy of a given playlist.'


logger = get_logger()


# Parse command line arguments
def parse_args():
	logger.debug('Parsing arguments')

	parser = argparse.ArgumentParser(prog=__SCRIPT_NAME, description=__SCRIPT_DESC)

	parser.add_argument('client_id', help=ARG_DESCS['client_id'])
	parser.add_argument('client_secret', help=ARG_DESCS['client_secret'])
	parser.add_argument('access_token', help=ARG_DESCS['access_token'])
	parser.add_argument('refresh_token', help=ARG_DESCS['refresh_token'])
	parser.add_argument('input_playlist_id', help=ARG_DESCS['input_playlist_id'])
	parser.add_argument('output_playlist_name', help=ARG_DESCS['output_playlist_name'])
	parser.add_argument(
		'--debug', '-d', help=ARG_DESCS['debug'], default=False, action='store_true'
	)

	args = parser.parse_args()

	if args.debug:
		enable_debug_logging(logger)

	assert_valid_client_id(args.client_id)
	assert_valid_client_secret(args.client_secret)
	assert_valid_access_token(args.access_token)
	assert_valid_refresh_token(args.refresh_token)
	assert_valid_input_playlist_id(args.input_playlist_id)
	assert_valid_output_playlist_name(args.output_playlist_name)

	return args


# Get a list of track IDs from a playlist
def get_playlist_track_ids(sp, playlist_id):
	logger.debug(f'Getting track IDs for playlist {playlist_id}')

	chunk_size = 100
	chunk_offset = 0
	track_ids = []

	while True:
		chunked_tracks = sp.playlist_tracks(
			playlist_id,
			fields='items(track(id))',
			limit=chunk_size,
			offset=chunk_offset,
		)['items']

		if not chunked_tracks:
			logger.debug(f'{len(track_ids)} track IDs found')
			break

		track_ids.extend(list(map(lambda track: track['track']['id'], chunked_tracks)))

		chunk_offset += chunk_size

	return track_ids


# Create a new playlist with the given name and add tracks to it
def create_playlist(sp, user_id, playlist_name, track_ids):
	logger.debug(f'Creating new playlist "{playlist_name}"')

	ts = datetime.now()
	readable_ts = ts.strftime('%F %R')
	playlist_name = ts.strftime(playlist_name)
	playlist = sp.user_playlist_create(
		user_id,
		playlist_name,
		public=False,
		collaborative=False,
		description=f'Playlist last updated on {readable_ts} by {APP_NAME} ({APP_URL})',
	)

	sp.playlist_add_items(playlist['id'], track_ids)

	logger.debug(f'Playlist created: {playlist}')


# Script entry point
def main():
	logger.debug('Script started')

	args = parse_args()
	cache_handler = CacheArgHandler(SCOPE, args.access_token, args.refresh_token)
	sp = authorize(
		SCOPE, args.client_id, args.client_secret, REDIRECT_URI, cache_handler
	)
	user_id = sp.me()['id']
	track_ids = get_playlist_track_ids(sp, args.input_playlist_id)

	create_playlist(sp, user_id, args.output_playlist_name, track_ids)

	logger.debug('Script finished')


main()
