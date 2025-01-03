import argparse
from utils.constants import ARG_DESCS, SCOPE, REDIRECT_URI, TOKENS_FILENAME
from utils.logging import get_logger, enable_debug_logging
from utils.auth import authorize
from utils.cache import CacheArgHandler
from utils.validation import (
	get_client_creds_arg_parser,
	assert_valid_client_creds,
)


# Constants
__SCRIPT_NAME = 'setup.py'
__SCRIPT_DESC = 'Grant access to your Spotify account and save the access and refresh tokens to a file.'


logger = get_logger()


# Parse command line arguments
def parse_args():
	logger.debug('Parsing arguments')

	args = argparse.ArgumentParser(
		parents=[get_client_creds_arg_parser()],
		prog=__SCRIPT_NAME,
		description=__SCRIPT_DESC,
	).parse_args()

	if args.debug:
		enable_debug_logging(logger)

	assert_valid_client_creds(args.client_id, args.client_secret)

	return args


# Save tokens to a file
def save_tokens_to_file(token_info):
	if not token_info:
		raise ValueError(
			'Something went wrong. Expected token info to be defined but it was not'
		)
	try:
		file = open(TOKENS_FILENAME, 'w')
		file.write(
			f'SPOTIFY_ACCESS_TOKEN: {token_info["access_token"]}\nSPOTIFY_REFRESH_TOKEN: {token_info["refresh_token"]}'
		)
		file.close()
	except IOError:
		logger.warning(f"Couldn't write tokens to {TOKENS_FILENAME}")

	logger.info(
		f'Tokens were saved to {TOKENS_FILENAME}. Do not push this file to GitHub'
	)


# Script entry point
def main():
	logger.debug('Script started')

	args = parse_args()
	cache_handler = CacheArgHandler(SCOPE)

	logger.info('Opening browser to authorize with Spotify')

	sp = authorize(
		SCOPE, args.client_id, args.client_secret, REDIRECT_URI, cache_handler, True
	)
	# Dummy API call to force token refresh
	sp.me()['id']
	save_tokens_to_file(cache_handler.get_cached_token())

	logger.debug('Script finished')


main()
