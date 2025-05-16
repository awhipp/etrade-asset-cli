"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function
import os
import pyetrade
from dotenv import load_dotenv
import webbrowser
class Client:

    env_type: str = ""
    dev_type: bool = False
    consumer_key: str = ""
    consumer_secret: str = ""
    base_url: str = ""
    oauth_token: str = ""
    oauth_token_secret: str = ""

    def __init__(self, skip_tokens=False):
        # loading configuration file if exists
        if os.path.exists(".env"):
            # Clear environment variables
            print("Clearing environment variables as .env file exists.")
            os.environ.pop("OAUTH_TOKEN", None)
            os.environ.pop("OAUTH_TOKEN_SECRET", None)
            load_dotenv()

        self.env_type = os.getenv("ENV_TYPE", "sandbox")

        if self.env_type == "sandbox":
            self.dev_type = True
            self.consumer_key = os.getenv("SANDBOX_CONSUMER_KEY")
            self.consumer_secret = os.getenv("SANDBOX_CONSUMER_SECRET")
            self.base_url = os.getenv("SANDBOX_BASE_URL")
        else:
            self.dev_type = False
            self.consumer_key = os.getenv("PROD_CONSUMER_KEY")
            self.consumer_secret = os.getenv("PROD_CONSUMER_SECRET")
            self.base_url = os.getenv("PROD_BASE_URL")

        # OAuth tokens
        self.oauth_token = os.getenv("OAUTH_TOKEN", "")
        self.oauth_token_secret = os.getenv("OAUTH_TOKEN_SECRET", "")

        if not skip_tokens and (not self.oauth_token or not self.oauth_token_secret):
            self.get_tokens()

    def get_params(self):
        '''
        This function returns the parameters for the E*TRADE API
        '''
        return  {
            'client_key': self.consumer_key,
            'client_secret': self.consumer_secret,
            'resource_owner_key': self.oauth_token,
            'resource_owner_secret': self.oauth_token_secret
        }
    
    def update_env_file(self, key, value):
        '''
        This function removes the key from the .env file and adds the new key-value pair
        '''
        with open(".env", "r", encoding='utf-8') as env_file:
            lines = env_file.readlines()

        with open(".env", "w", encoding='utf-8') as env_file:
            for line in lines:
                if key in line:
                    continue
                env_file.write(line)
            env_file.write(f"\n{key}={value}")

    def get_tokens(self):
        '''
        This function generates the OAuth tokens for the E*TRADE API
        '''
        oauth = pyetrade.ETradeOAuth(self.consumer_key, self.consumer_secret)
        URL = oauth.get_request_token() # Use the returned URL
        print(f"Go to the following URL to authorize the app: {URL}")

        # Open browser
        webbrowser.open(URL)
        
        verifier_code = input("Enter the verifier code: ")
        print(f"Verifier code: {verifier_code}")
        tokens = oauth.get_access_token(verifier_code)

        self.oauth_token = tokens['oauth_token']
        self.oauth_token_secret = tokens['oauth_token_secret']
        
        # Save the tokens for future use
        self.update_env_file("OAUTH_TOKEN", self.oauth_token)
        self.update_env_file("OAUTH_TOKEN_SECRET", self.oauth_token_secret)

        return self.oauth_token, self.oauth_token_secret
    
    def renew_tokens(self):
        '''
        This function renews the OAuth tokens for the E*TRADE API
        '''
        oauth = pyetrade.ETradeAccessManager(**self.get_params())
        return oauth.renew_access_token()


    def get_account(self):
        '''
        This function gets the account ID key for the E*TRADE API
        '''
        accounts = pyetrade.ETradeAccounts(**self.get_params(), dev=self.dev_type)
        account = accounts.list_accounts()['AccountListResponse']['Accounts']['Account']
        return account
    

    def get_account_balance(self, account_id_key):
        '''
        This function gets the account balance for the account
        '''
        account = pyetrade.ETradeAccounts(**self.get_params(), dev=self.dev_type)
        balance = account.get_account_balance(account_id_key=account_id_key)
        return round(float(balance['BalanceResponse']['Computed']['cashAvailableForInvestment']), 2)
    
    def get_positions(self, account_id_key):
        '''
        This function gets the positions for the account
        '''
        account = pyetrade.ETradeAccounts(**self.get_params(), dev=self.dev_type)
        return account.get_account_portfolio(account_id_key=account_id_key)

    def get_market_quote(self, symbols):
        '''
        This function gets the market quotes for the symbols
        '''
        market = pyetrade.ETradeMarket(**self.get_params(), dev=self.dev_type)
        return market.get_quote(symbols)

    def list_orders(self, account_id_key):
        '''
        This function lists the orders for the account
        '''
        order = pyetrade.ETradeOrder(**self.get_params(), dev = self.dev_type)
        return order.list_orders(account_id_key=account_id_key)

    def get_option_chains(self, symbol, strike_price=None, expiry_date=None):
        '''
        This function gets the option chains for a symbol using the E*TRADE API
        
        Parameters:
        - symbol: The ticker symbol (underlier)
        - strike_price: Optional - The target strike price
        - expiry_date: Optional - The expiration date as a datetime.date object
        
        Returns option chain data for the symbol
        '''
        market = pyetrade.ETradeMarket(**self.get_params(), dev=self.dev_type)
        
        # Set parameters according to API documentation
        params = {
            'underlier': symbol,
            'chain_type': None,  # Get both calls and puts
            'no_of_strikes': 1,
            'resp_format': 'json',
        }
        
        # Add optional parameters if provided
        if strike_price:
            params['strike_price_near'] = strike_price

        # None is a valid value for expiry_date, so check if it's provided    
        params['expiry_date'] = expiry_date

        # Call the API to get option chains
        print(f"Getting option chains for {symbol} with params: {params}")
            
        return market.get_option_chains(**params)