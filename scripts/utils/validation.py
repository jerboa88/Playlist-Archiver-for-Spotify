__CLIENT_ID_LENGTH = 32
__PLAYLIST_ID_LENGTH = 22


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


# Check if a client ID is valid
def assert_valid_client_id(client_id):
	__assert_non_empty('client ID', client_id)
	__assert_length('client ID', client_id, __CLIENT_ID_LENGTH)


# Check if a client secret is valid
def assert_valid_client_secret(client_secret):
	__assert_non_empty('client secret', client_secret)
	__assert_length('client secret', client_secret, __CLIENT_ID_LENGTH)


# Check if a client secret is valid
def assert_valid_access_token(access_token):
	__assert_non_empty('access token', access_token)


# Check if a client secret is valid
def assert_valid_refresh_token(refresh_token):
	__assert_non_empty('refresh token', refresh_token)


# Check if playlist names are valid
def assert_valid_playlist_names(playlist_names):
	__assert_non_empty('playlist names', playlist_names)


# Check if an input playlist ID is valid
def assert_valid_input_playlist_id(input_playlist_id):
	__assert_non_empty('input playlist ID', input_playlist_id)
	__assert_length('input playlist ID', input_playlist_id, __PLAYLIST_ID_LENGTH)


# Check if an output playlist name is valid
def assert_valid_output_playlist_name(output_playlist_name):
	__assert_non_empty('output playlist name', output_playlist_name)
