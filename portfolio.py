from client import Client

BASE_ASSET: dict = {
    'current_allocation': 0.0,
    'target_allocation': 0.0,
    'portfolio_value': 0.0,
    'current_price': 0.0,
    'shares': 0
}

DIVIDENDS: list = ['IQQQ', 'ISPY', 'SPYI', 'QQQI', 'JEPQ', 'JEPI']

class Portfolio:

    client: Client
    account: dict
    account_id_key: str
    balance: dict = {
        'cash': 0.0,
        'asset_value': 0.0,
    }
    assets: dict = {
        'SCHB': { # Broad Market (30%)
            **BASE_ASSET,
            'target_allocation': 0.30
        },
        'SCHF': { # International (15%)
            **BASE_ASSET,
            'target_allocation': 0.15
        },
        'SCHZ': { # Bonds (5%)
            **BASE_ASSET,
            'target_allocation': 0.05
        },
        # DIVIDENDS added here
    }

    def __init__(self, client: Client):
        self.client = client
        self.account = self.client.get_account()
        self.account_id_key = self.account['accountIdKey']
        
        self.balance['cash'] = self.client.get_account_balance(self.account_id_key)

        self.add_dividends_to_assets()

        self.get_current_assets() # Must be first
        self.get_asset_prices()
        self.calculate_portfolio_value()

    def add_dividends_to_assets(self):
        '''
        Add dividends to the assets dictionary with target allocation for the remaining 50%.
        '''
        remaining_allocation = 0.50
        dividend_allocation = remaining_allocation / len(DIVIDENDS)
        for dividend in DIVIDENDS:
            self.assets[dividend] = {
                **BASE_ASSET,
                'target_allocation': dividend_allocation
            }

    def print_allocation(self):
        '''
        Print allocation details: stock, current, target, difference in percentage.
        '''
        print(f"{'Stock':<10}{'Current':>10}{'Target':>10}{'Difference':>10}")
        for symbol, data in self.assets.items():
            print(f"{symbol:<10}{data['current_allocation']*100:>10.2f}%{data['target_allocation']*100:>10.2f}%{data['current_allocation']-data['target_allocation']:>10.2f}")

    def get_current_assets(self):
        '''
        Get the current assets in the portfolio.
        '''
        positions = self.client.get_positions(self.account_id_key)
        positions = positions['PortfolioResponse']['AccountPortfolio']['Position']
        for position in positions:
            symbol = position['Product']['symbol']
            quantity = position['quantity']
            if symbol in self.assets:
                self.assets[symbol]['shares'] = quantity
            else:
                print(f"Skipping {symbol} as it is not in the core portfolio.")

    def get_asset_prices(self):
        '''
        Get the current price of the assets in the portfolio.
        '''
        market_quotes = self.client.get_market_quote(list(self.assets.keys()))
        quote_data = market_quotes['QuoteResponse']['QuoteData']
        for data in quote_data:
            symbol = data['Product']['symbol']
            last_trade_price = data['All']['lastTrade']
            self.assets[symbol]['current_price'] = last_trade_price

    def calculate_portfolio_value(self):
        '''
        Calculate the portfolio value.
        '''
        # Calculate the asset value
        for symbol, data in self.assets.items():
            self.balance['asset_value'] += float(data['current_price']) * float(data['shares'])
            self.assets[symbol]['value'] = float(data['current_price']) * float(data['shares'])

        # Calculate current allocation
        for symbol, data in self.assets.items():
            self.assets[symbol]['current_allocation'] = round(data['value'] / self.balance['asset_value'], 2)
        

    def list_orders(self):
        '''
        List all the orders for the account.
        '''
        orders = self.client.get_orders(self.account_id_key)
        return orders
    
    def calculate_purchases(self):
        '''
        Calculate the purchases based on the available funds.
        '''
        print(f"Available funds: {self.balance['cash']}")
        for symbol, data in self.assets.items():
            target_value = round(float(data['target_allocation'] * self.balance['cash']), 2)
            if data['value'] < target_value:
                # Calculate the number of shares to purchase
                price = round(float(data['current_price']), 2)
                shares = (target_value - data['value']) / price
                print(f"Buy {int(shares)} shares of {symbol} at {price} (total of ~{target_value})")