import argparse
from datetime import datetime
from common import CONSTANTS, debug, warn, CacheArgHandler, authorize


# Vars
is_debug_mode = False


# Parse command line arguments
def parse_args(app_name, app_desc):
	debug('Parsing arguments')

	descriptions = {
		'client_id': 'Your client ID for Spotify. A client ID is required for this program to work',
		'client_secret': f'Your client secret for Spotify. A client secret is required for this program to work',
		'access_token': f'Your access token for Spotify. This can be found in {CONSTANTS["tokens_filename"]} after the program is run for the first time',
		'refresh_token': f'Your refresh token for Spotify. This can be found in {CONSTANTS["tokens_filename"]} after the program is run for the first time',
		'input_playlist_name': 'The name of the playlist you want to make a copy of. The name must match exactly. This is required',
		'output_playlist_name': 'The name of the output playlist. strftime format codes can be used to include the date/time in the name. This is required',
		'debug': 'Whether to print additional information to the console for debugging. Default: false',
	}
	parser = argparse.ArgumentParser(prog=app_name, description=app_desc)

	parser.add_argument('client_id', help=descriptions['client_id'])
	parser.add_argument('client_secret', help=descriptions['client_secret'])
	parser.add_argument('access_token', help=descriptions['access_token'])
	parser.add_argument('refresh_token', help=descriptions['refresh_token'])
	parser.add_argument('input_playlist_name', help=descriptions['input_playlist_name'])
	parser.add_argument('output_playlist_name', help=descriptions['output_playlist_name'])
	parser.add_argument('--debug', '-d', help=descriptions['debug'], default=False, action='store_true')

	args = parser.parse_args()

	# Check client ID
	if args.client_id:
		if len(args.client_id) != 32:
			raise ValueError('The entered client ID is invalid. It must be 32 characters long')

	# Check client secret
	if args.client_secret:
		if len(args.client_secret) != 32:
			raise ValueError('The entered client secret is invalid. It must be 32 characters long')

	# Check access token
	if not args.access_token:
		raise ValueError('The entered access token is invalid')

	# Check refresh token
	if not args.refresh_token:
		raise ValueError('The entered refresh token is invalid')

	# Check input playlist name
	if not args.input_playlist_name:
		raise ValueError('The input playlist name cannot be empty')

	# Check output playlist name
	if not args.output_playlist_name:
		raise ValueError('The output playlist name cannot be empty')

	return args


# Get the ID of a playlist given its name
def get_playlist_id(sp, playlist_name):
	debug(f'Getting playlist id for {playlist_name}')

	chunk_size = 50
	chunk_offset = 0
	playlist_id = None
	playlist_names = []

	while not playlist_id:
		chunked_playlists = sp.current_user_playlists(limit=chunk_size, offset=chunk_offset)['items']

		if not chunked_playlists:
			debug('Finished searching through playlists')
			break

		for playlist in chunked_playlists:
			if playlist['name'] == playlist_name:
				playlist_id = playlist['id']
				debug(f'Playlist id of {playlist_name} is {playlist_id}')
				break
			else:
				playlist_names.append(playlist['name'])

		chunk_offset += chunk_size

	if not playlist_id:
		playlist_names.sort()
		formatted_playlist_names = '\n  '.join(playlist_names)
		raise ValueError(f'Playlist "{playlist_name}" not found. Is the playlist name correct? Available playlists:\n  {formatted_playlist_names}')

	return playlist_id


# Get a list of track IDs from a playlist
def get_playlist_track_ids(sp, playlist_id):
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


# Create a new playlist with the given name and add tracks to it
def create_playlist(sp, user_id, playlist_name, track_ids, app_name):
	debug(f'Creating new playlist {playlist_name}')

	ts = datetime.now()
	playlist_name = ts.strftime(playlist_name)
	playlist = sp.user_playlist_create(user_id, playlist_name, public=False, collaborative=False, description=f'Playlist created by {app_name} on {ts}')

	sp.playlist_add_items(playlist['id'], track_ids)

	debug(f'Playlist created: {playlist}')


# Script entry point
def main():
	print('Script started')

	args = parse_args(CONSTANTS['app_name'], CONSTANTS['app_desc'])
	is_debug_mode = args.debug
	cache_handler = CacheArgHandler(CONSTANTS['scope'], args.access_token, args.refresh_token)
	sp = authorize(CONSTANTS['scope'], args.client_id, args.client_secret, CONSTANTS['redirect_uri'], cache_handler)
	user_id = sp.me()['id']
	playlist_id = get_playlist_id(sp, args.input_playlist_name)
	track_ids = get_playlist_track_ids(sp, playlist_id)

	create_playlist(sp, user_id, args.output_playlist_name, track_ids, CONSTANTS['app_name'])

	print('Script finished')


main()
