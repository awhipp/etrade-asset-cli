import argparse
from client import Client
from spy_strategy import SpyStrategy

parser = argparse.ArgumentParser(description="E*TRADE API Client")
parser.add_argument('--new-token', action='store_true', help="Get new OAuth tokens")
parser.add_argument('--refresh-token', action='store_true', help="Refresh the OAuth token")
parser.add_argument('--spy-strat', action='store_true', help="Run SPY options strategy analysis")
args = parser.parse_args()


if args.new_token:
    client = Client(skip_tokens=True)
    client.get_tokens()
    print("OAuth token retrieved successfully.")
else:
    client = Client()
    if args.refresh_token:
        client.renew_tokens()
        print("OAuth token refreshed successfully.")
    elif args.spy_strat:
        spy_strategy = SpyStrategy(client)
        spy_strategy.run_strategy()
    else:
        print("No valid option provided. Use --help for more information.")
