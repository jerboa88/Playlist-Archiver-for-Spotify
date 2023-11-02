import argparse
from common import CONSTANTS, debug, warn, CacheArgHandler, authorize


# Vars
tokens_save_msg = f'Please create GitHub secrets for both of these tokens. Do not push this file to GitHub'
is_debug_mode = False


# Save tokens to a file
def save_tokens_to_file(token_info):
	if not token_info:
		raise ValueError('Something went wrong. Expected token info to be defined but it was not')
	try:
		f = open(CONSTANTS['tokens_filename'], 'w')
		f.write(f'# {tokens_save_msg}\nSPOTIFY_ACCESS_TOKEN: {token_info["access_token"]}\nSPOTIFY_REFRESH_TOKEN: {token_info["refresh_token"]}')
		f.close()
	except IOError:
		warn(f'Couldn\'t write tokens to cache to: {CONSTANTS["tokens_filename"]}')

	print(f'Tokens were saved to {CONSTANTS["tokens_filename"]}. {tokens_save_msg}')


# Parse command line arguments
def parse_args(app_name, app_desc):
	debug('Parsing arguments', is_debug_mode)

	descriptions = {
		'client_id': 'Your client ID for Spotify. A client ID is required for this program to work',
		'client_secret': f'Your client secret for Spotify. A client secret is required for this program to work',
		'debug': 'Whether to print additional information to the console for debugging. Default: false',
	}
	parser = argparse.ArgumentParser(prog=app_name, description=app_desc)

	parser.add_argument('client_id', help=descriptions['client_id'])
	parser.add_argument('client_secret', help=descriptions['client_secret'])
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

	return args


# Script entry point
def main():
	print('Script started')

	args = parse_args(CONSTANTS['app_name'], CONSTANTS['app_desc'])
	is_debug_mode = args.debug
	cache_handler = CacheArgHandler(CONSTANTS['scope'])

	print('Opening browser to authorize with Spotify')

	sp = authorize(CONSTANTS['scope'], args.client_id, args.client_secret, CONSTANTS['redirect_uri'], cache_handler, True)
	# Dummy API call to force token refresh
	sp.me()['id']
	save_tokens_to_file(cache_handler.get_cached_token())

	print('Script finished')


main()
