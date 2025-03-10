import argparse
from client import Client
from portfolio import Portfolio

parser = argparse.ArgumentParser(description="E*TRADE API Client")
parser.add_argument('--new-token', action='store_true', help="Get new OAuth tokens")
parser.add_argument('--refresh-token', action='store_true', help="Refresh the OAuth token")
parser.add_argument('--view-allocation', action='store_true', help="View Allocation")
parser.add_argument('--calc-allocation', action='store_true', help="Calculate Allocation")
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
    elif args.view_allocation:
        portfolio = Portfolio(client)
        portfolio.print_allocation()
    elif args.calc_allocation:
        portfolio = Portfolio(client)
        available_funds = float(client.get_account_balance(portfolio.account_id_key))
        portfolio.calculate_purchases()
    else:
        print("No valid option provided. Use --help for more information.")
