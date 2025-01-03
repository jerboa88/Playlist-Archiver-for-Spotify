from argparse import ArgumentParser
from utils.constants import ARG_DESCS, SAVED_TRACKS_KEYWORD


# Constants
__CLIENT_ID_LENGTH = 32
__PLAYLIST_ID_LENGTH = 22


# Get an argument parser for client credentials
def get_client_creds_arg_parser():
	parser = ArgumentParser(add_help=False)

	parser.add_argument('client_id', help=ARG_DESCS['client_id'])
	parser.add_argument('client_secret', help=ARG_DESCS['client_secret'])
	parser.add_argument(
		'--debug', '-d', help=ARG_DESCS['debug'], default=False, action='store_true'
	)

	return parser


# Get an argument parser for client credentials and access/refresh tokens
def get_tokens_arg_parser():
	parent_parser = get_client_creds_arg_parser()
	parser = ArgumentParser(add_help=False, parents=[parent_parser])

	parser.add_argument('access_token', help=ARG_DESCS['access_token'])
	parser.add_argument('refresh_token', help=ARG_DESCS['refresh_token'])

	return parser


# Check that a value is not empty
def __assert_non_empty(value_name, value):
	if not value:
		raise ValueError(f'The {value_name} cannot be empty')


# Check that a value is of the expected length
def __assert_length(value_name, value, length):
	if len(value) != length:
		raise ValueError(
			f'The entered {value_name} is invalid. It must be {length} characters long'
		)


# Check if client credentials are valid
def assert_valid_client_creds(client_id, client_secret):
	__assert_non_empty('client ID', client_id)
	__assert_length('client ID', client_id, __CLIENT_ID_LENGTH)
	__assert_non_empty('client secret', client_secret)
	__assert_length('client secret', client_secret, __CLIENT_ID_LENGTH)


# Check if access and refresh tokens are valid
def assert_valid_tokens(access_token, refresh_token):
	__assert_non_empty('access token', access_token)
	__assert_non_empty('refresh token', refresh_token)


# Check if playlist names are valid
def assert_valid_playlist_names(playlist_names):
	__assert_non_empty('playlist names', playlist_names)


# Check if an input playlist ID is valid
def assert_valid_input_playlist_id(input_playlist_id):
	__assert_non_empty('input playlist ID', input_playlist_id)

	# Skip length check if the input playlist ID is the 'saved_tracks' keyword
	if input_playlist_id != SAVED_TRACKS_KEYWORD:
		__assert_length('input playlist ID', input_playlist_id, __PLAYLIST_ID_LENGTH)


# Check if an output playlist name is valid
def assert_valid_output_playlist_name(output_playlist_name):
	__assert_non_empty('output playlist name', output_playlist_name)
