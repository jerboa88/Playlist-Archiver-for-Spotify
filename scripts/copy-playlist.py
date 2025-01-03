import argparse
import threading
import queue
from tqdm import tqdm
from datetime import datetime
from utils.constants import (
	APP_NAME,
	APP_URL,
	ARG_DESCS,
	SCOPE,
	REDIRECT_URI,
	SAVED_TRACKS_KEYWORD,
)
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
__CHUNK_SIZE_FOR_FETCH = 50
__CHUNK_SIZE_FOR_ADD = 100
__PROGRESS_BAR_UNIT = ' tracks'
__PROGRESS_BAR_COLOUR = '#1ED760'
__PLAYLIST_TRACK_LIMIT = 10000


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
		'--visibility',
		choices=['auto', 'private', 'public'],
		default='auto',
		help=ARG_DESCS['--contributions'],
	)
	parser.add_argument(
		'--contributions',
		choices=['auto', 'individual', 'collaborative'],
		default='auto',
		help=ARG_DESCS['--contributions'],
	)
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


# Fetch the metadata for a given playlist (fetch_fn, total_tracks, is_public, is_collaborative)
def fetch_playlist_details(sp, input_playlist_id):
	if input_playlist_id == SAVED_TRACKS_KEYWORD:
		return (
			fetch_chunk_of_saved_tracks,
			fetch_chunk_of_saved_tracks(sp, input_playlist_id, 0, 1)['total'],
			False,
			False,
		)
	else:
		input_playlist = sp.playlist(
			input_playlist_id, fields='collaborative,public,tracks.total'
		)

		return (
			fetch_chunk_of_playlist_tracks,
			input_playlist['tracks']['total'],
			input_playlist['public'],
			input_playlist['collaborative'],
		)


# Create a new playlist with the given name
def create_playlist(
	sp,
	user_id,
	playlist_name,
	is_public,
	is_collaborative,
):
	logger.debug(f'Creating new playlist "{playlist_name}"')

	ts = datetime.now()
	readable_ts = ts.strftime('%F %R')
	playlist_name = ts.strftime(playlist_name)
	playlist = sp.user_playlist_create(
		user_id,
		playlist_name,
		public=is_public,
		collaborative=is_collaborative,
		description=f'Playlist last updated on {readable_ts} by {APP_NAME} ({APP_URL})',
	)

	logger.debug(f'Playlist created: {playlist}')

	return playlist['id']


# Fetch a page of playlist track IDs from the Spotify API
def fetch_chunk_of_playlist_tracks(
	sp, playlist_id, chunk_offset, limit=__CHUNK_SIZE_FOR_FETCH
):
	return sp.playlist_tracks(
		playlist_id, fields='items(track(id))', limit=limit, offset=chunk_offset
	)


# Fetch a page of saved track IDs from the Spotify API
def fetch_chunk_of_saved_tracks(sp, _, chunk_offset, limit=__CHUNK_SIZE_FOR_FETCH):
	return sp.current_user_saved_tracks(limit=limit, offset=chunk_offset)


# Fetch a list of track IDs for a playlist and add them to the queue
def fetch_playlist_tracks(
	sp, track_ids_queue, playlist_id, fetch_fn, total_num_of_tracks
):
	logger.debug(f'Getting track IDs for playlist {playlist_id}')

	chunk_offset = 0

	with tqdm(
		unit=__PROGRESS_BAR_UNIT,
		colour=__PROGRESS_BAR_COLOUR,
		position=0,
		desc='📥 Fetching tracks from playlist',
		total=total_num_of_tracks,
	) as progress_bar:
		while True:
			chunked_tracks = fetch_fn(sp, playlist_id, chunk_offset)['items']

			# If there are no more tracks, exit the loop
			if not chunked_tracks:
				break

			chunked_track_ids = list(
				map(lambda track: track['track']['id'], chunked_tracks)
			)
			num_of_tracks_in_chunk = len(chunked_track_ids)

			# Add a chunk of track IDs to the queue
			for track_id in chunked_track_ids:
				track_ids_queue.put(track_id)

			logger.debug(f'Fetched {num_of_tracks_in_chunk} tracks from playlist')

			progress_bar.update(num_of_tracks_in_chunk)

			chunk_offset += __CHUNK_SIZE_FOR_FETCH

	# Add a sentinel value to the queue to indicate that the producer is done
	track_ids_queue.put(None)

	logger.debug('Finished fetching tracks from playlist')


# Get track IDs from the queue and add them to the output playlist
def add_tracks_to_playlist(
	sp,
	track_ids_queue,
	output_playlist_id,
	total_num_of_tracks,
):
	is_waiting_on_jobs = True

	with tqdm(
		unit=__PROGRESS_BAR_UNIT,
		colour=__PROGRESS_BAR_COLOUR,
		position=1,
		desc='📤 Adding tracks to playlist',
		total=total_num_of_tracks,
	) as progress_bar:
		while is_waiting_on_jobs:
			chunked_track_ids = []

			# Get a chunk of track IDs to include in the API call
			for _ in range(__CHUNK_SIZE_FOR_ADD):
				track_id = track_ids_queue.get()

				if not track_id:
					is_waiting_on_jobs = False

					break

				chunked_track_ids.append(track_id)

			num_of_tracks_in_chunk = len(chunked_track_ids)

			sp.playlist_add_items(output_playlist_id, chunked_track_ids)

			logger.debug(f'Added {num_of_tracks_in_chunk} tracks to playlist')

			progress_bar.update(num_of_tracks_in_chunk)

			# Mark the jobs as done
			for _ in chunked_track_ids:
				track_ids_queue.task_done()

	logger.debug('Finished adding tracks to playlist')

	# Mark the sentinel value as done
	track_ids_queue.task_done()


# Entry point
def main():
	logger.debug('Script started')

	args = parse_args()
	cache_handler = CacheArgHandler(SCOPE, args.access_token, args.refresh_token)
	sp = authorize(
		SCOPE, args.client_id, args.client_secret, REDIRECT_URI, cache_handler
	)
	user_id = sp.me()['id']
	(
		fetch_fn,
		input_playlist_num_of_tracks,
		is_input_playlist_public,
		is_input_playlist_collaborative,
	) = fetch_playlist_details(sp, args.input_playlist_id)

	if input_playlist_num_of_tracks >= __PLAYLIST_TRACK_LIMIT:
		logger.warning(
			f'The input playlist has {input_playlist_num_of_tracks} tracks, but Spotify allows a maximum of {__PLAYLIST_TRACK_LIMIT} tracks in a playlist. We might not be able to copy them all'
		)

	is_public = args.visibility == 'public' or (
		args.visibility == 'auto' and is_input_playlist_public
	)
	is_collaborative = args.contributions == 'collaborative' or (
		args.contributions == 'auto' and is_input_playlist_collaborative
	)
	output_playlist_id = create_playlist(
		sp,
		user_id,
		args.output_playlist_name,
		is_public,
		is_collaborative,
	)
	track_ids_queue = queue.Queue()

	threading.Thread(
		target=fetch_playlist_tracks,
		args=(
			sp,
			track_ids_queue,
			args.input_playlist_id,
			fetch_fn,
			input_playlist_num_of_tracks,
		),
		daemon=True,
	).start()
	add_tracks_to_playlist(
		sp,
		track_ids_queue,
		output_playlist_id,
		input_playlist_num_of_tracks,
	)
	track_ids_queue.join()

	logger.debug('Script finished')


main()
