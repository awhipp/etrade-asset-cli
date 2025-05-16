"""
This module implements the SPY strategy functionality for the E*TRADE CLI.
The strategy gets the current price of SPY and finds option chains closest to that price.
"""

import datetime
from typing import Dict, Any

class SpyStrategy:
    """
    A class to implement the SPY options strategy
    """
    
    def __init__(self, client):
        """
        Initialize the SPY strategy with the E*TRADE client
        """
        self.client = client
        self.spy_symbol = 'SPY'
        self.spy_price = None
        self.option_data = None
    
    def run_strategy(self):
        """
        Execute the SPY strategy:
        1. Get current SPY price
        2. Find closest option chain
        3. Get CALL and PUT prices
        """
        # Step 1: Get current SPY price
        self._get_current_price()
        
        if not self.spy_price:
            print(f"Failed to get current price for {self.spy_symbol}")
            return None
        
        print(f"Current {self.spy_symbol} price: ${self.spy_price}")
        
        # Step 2: Get option chains closest to current price
        self._get_option_chains()
        
        # Step 3: Display the relevant options
        self._display_options()
        
        return self.option_data
    
    def _get_current_price(self):
        """
        Get the current SPY price from the market
        """
        try:
            # Get the market quote for SPY
            quote = self.client.get_market_quote([self.spy_symbol])
            
            # Handle different response structures with better error handling
            if 'QuoteResponse' in quote and 'QuoteData' in quote['QuoteResponse']:
                quote_data = quote['QuoteResponse']['QuoteData']
                
                # Handle list or direct object
                if isinstance(quote_data, list) and len(quote_data) > 0:
                    data = quote_data[0]
                else:
                    data = quote_data
                    
                # Try multiple possible paths to extract price
                if 'All' in data and 'lastTrade' in data['All']:
                    self.spy_price = float(data['All']['lastTrade'])
                elif 'All' in data and 'price' in data['All']:
                    self.spy_price = float(data['All']['price'])
                elif 'Intraday' in data and 'lastPrice' in data['Intraday']:
                    self.spy_price = float(data['Intraday']['lastPrice'])
                
                # If still no price, try to print available keys for debugging
                if not self.spy_price and 'All' in data:
                    print(f"DEBUG: Available price fields: {data['All'].keys()}")
                    if 'lastPrice' in data['All']:
                        self.spy_price = float(data['All']['lastPrice'])
            else:
                print(f"DEBUG: Unexpected quote structure. Available keys: {quote.keys()}")
                
        except (KeyError, IndexError, ValueError, AttributeError) as e:
            print(f"Error getting {self.spy_symbol} price: {e}")
            self.spy_price = None
    
    def _get_option_chains(self):
        """
        Get option chains for SPY at the current price
        """
        try:
            # Get option chains data using correct parameters
            option_chains = self.client.get_option_chains(
                symbol=self.spy_symbol, 
                strike_price=self.spy_price
            )
            
            # Process the option chain response
            self.option_data = self._process_option_chain(option_chains)
        except Exception as e:
            print(f"Error getting option chains: {e}")
            self.option_data = None
    
    def _process_option_chain(self, option_chains_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the option chain response to extract relevant data
        
        Args:
            option_chains_data: The option chains data from API
            
        Returns:
            Dict with call and put options data
        """
        try:
            # Extract the main response object
            if 'OptionChainResponse' not in option_chains_data:
                print("No OptionChainResponse in data")
                return {}
                
            chain_response = option_chains_data['OptionChainResponse']
            
            # Get expiry date from SelectedED if available
            expiry_date = None
            days_to_expiry = None
            
            if 'SelectedED' in chain_response:
                selected_date = chain_response['SelectedED']
                if all(key in selected_date for key in ['year', 'month', 'day']):
                    year = int(selected_date['year'])
                    month = int(selected_date['month'])
                    day = int(selected_date['day'])
                    expiry_date = datetime.date(year, month, day)
                    days_to_expiry = (expiry_date - datetime.date.today()).days
            
            # Get the option pair - could be a single item or a list
            option_pair = chain_response.get('OptionPair', [])
            if not isinstance(option_pair, list):
                option_pair = [option_pair]
                
            if not option_pair:
                print("No OptionPair found in response")
                return {}
                
            # Use the first option pair (closest to the target price)
            pair = option_pair[0]
            
            # Extract call and put data
            call_data = pair.get('Call', {})
            put_data = pair.get('Put', {})
            
            # Calculate straddle values
            call_last_price = call_data.get('lastPrice', 0)
            put_last_price = put_data.get('lastPrice', 0)
            call_bid = call_data.get('bid', 0)
            put_bid = put_data.get('bid', 0)
            call_ask = call_data.get('ask', 0)
            put_ask = put_data.get('ask', 0)
            strike_price = call_data.get('strikePrice', self.spy_price)
            
            # Calculate straddle price and break-even points
            straddle_price = round(float(call_last_price) + float(put_last_price), 2) if isinstance(call_last_price, (int, float)) and isinstance(put_last_price, (int, float)) else 'N/A'
            
            # Calculate break-even bounds and distance if we have valid data
            break_even_lower = None
            break_even_upper = None
            break_even_distance = None
            
            if isinstance(strike_price, (int, float)) and isinstance(straddle_price, (int, float)):
                break_even_lower = round(float(strike_price) - float(straddle_price), 2)
                break_even_upper = round(float(strike_price) + float(straddle_price), 2)
                break_even_distance = round(float(straddle_price), 2)
            
            # Create straddle info
            straddle = {
                'symbol': f"{call_data.get('symbol', 'SPY')} {strike_price} Straddle",
                'strike_price': strike_price,
                'last_price': straddle_price,
                'bid': round(float(call_bid) + float(put_bid), 2) if isinstance(call_bid, (int, float)) and isinstance(put_bid, (int, float)) else 'N/A',
                'ask': round(float(call_ask) + float(put_ask), 2) if isinstance(call_ask, (int, float)) and isinstance(put_ask, (int, float)) else 'N/A',
                'break_even_lower': break_even_lower,
                'break_even_upper': break_even_upper,
                'break_even_distance': break_even_distance
            }
            
            # Build result dictionary
            result = {
                'expiry_date': expiry_date.strftime('%Y-%m-%d') if expiry_date else 'Unknown',
                'days_to_expiry': days_to_expiry,
                'call': {
                    'symbol': call_data.get('displaySymbol', call_data.get('symbol', 'N/A')),
                    'strike_price': call_data.get('strikePrice', 'N/A'),
                    'last_price': call_data.get('lastPrice', 'N/A'),
                    'bid': call_data.get('bid', 'N/A'),
                    'ask': call_data.get('ask', 'N/A'),
                    'volume': call_data.get('volume', 'N/A'),
                    'open_interest': call_data.get('openInterest', 'N/A'),
                },
                'put': {
                    'symbol': put_data.get('displaySymbol', put_data.get('symbol', 'N/A')),
                    'strike_price': put_data.get('strikePrice', 'N/A'),
                    'last_price': put_data.get('lastPrice', 'N/A'),
                    'bid': put_data.get('bid', 'N/A'),
                    'ask': put_data.get('ask', 'N/A'),
                    'volume': put_data.get('volume', 'N/A'),
                    'open_interest': put_data.get('openInterest', 'N/A'),
                },
                'straddle': straddle
            }
            
            # Add Greeks if available
            if 'OptionGreeks' in call_data:
                result['call']['greeks'] = call_data['OptionGreeks']
                
            if 'OptionGreeks' in put_data:
                result['put']['greeks'] = put_data['OptionGreeks']
                
            return result
            
        except Exception as e:
            print(f"Error processing option chain: {e}")
            return {}
    
    def _display_options(self):
        """
        Display the current SPY price and option prices
        """
        if not self.option_data:
            print("No option data available.")
            return
            
        print("\n===== SPY STRATEGY RESULTS =====")
        print(f"Current SPY Price: ${self.spy_price}")
        print(f"Expiry Date: {self.option_data.get('expiry_date')}")
        print(f"Days to Expiry: {self.option_data.get('days_to_expiry')}")
        
        call = self.option_data.get('call', {})
        put = self.option_data.get('put', {})
        straddle = self.option_data.get('straddle', {})
        
        print("\nCALL OPTION:")
        print(f"Symbol: {call.get('symbol', 'N/A')}")
        print(f"Strike Price: ${call.get('strike_price', 'N/A')}")
        print(f"Last Price: ${call.get('last_price', 'N/A')}")
        print(f"Bid: ${call.get('bid', 'N/A')}")
        print(f"Ask: ${call.get('ask', 'N/A')}")
        print(f"Volume: {call.get('volume', 'N/A')}")
        print(f"Open Interest: {call.get('open_interest', 'N/A')}")
        
        # Display Greeks if available
        if 'greeks' in call:
            greeks = call['greeks']
            print("\nGreeks:")
            print(f"  Delta: {greeks.get('delta', 'N/A')}")
            print(f"  Gamma: {greeks.get('gamma', 'N/A')}")
            print(f"  Theta: {greeks.get('theta', 'N/A')}")
            print(f"  Vega: {greeks.get('vega', 'N/A')}")
            print(f"  IV: {greeks.get('iv', 'N/A')}")
        
        print("\nPUT OPTION:")
        print(f"Symbol: {put.get('symbol', 'N/A')}")
        print(f"Strike Price: ${put.get('strike_price', 'N/A')}")
        print(f"Last Price: ${put.get('last_price', 'N/A')}")
        print(f"Bid: ${put.get('bid', 'N/A')}")
        print(f"Ask: ${put.get('ask', 'N/A')}")
        print(f"Volume: {put.get('volume', 'N/A')}")
        print(f"Open Interest: {put.get('open_interest', 'N/A')}")
        
        # Display Greeks if available
        if 'greeks' in put:
            greeks = put['greeks']
            print("\nGreeks:")
            print(f"  Delta: {greeks.get('delta', 'N/A')}")
            print(f"  Gamma: {greeks.get('gamma', 'N/A')}")
            print(f"  Theta: {greeks.get('theta', 'N/A')}")
            print(f"  Vega: {greeks.get('vega', 'N/A')}")
            print(f"  IV: {greeks.get('iv', 'N/A')}")
            
        print("\nSTRADDLE OPTION:")
        print(f"Symbol: {straddle.get('symbol', 'N/A')}")
        print(f"Strike Price: ${straddle.get('strike_price', 'N/A')}")
        print(f"Last Price: ${straddle.get('last_price', 'N/A')}")
        print(f"Bid: ${straddle.get('bid', 'N/A')}")
        print(f"Ask: ${straddle.get('ask', 'N/A')}")
        print(f"Break Even Lower: ${straddle.get('break_even_lower', 'N/A')}")
        print(f"Break Even Upper: ${straddle.get('break_even_upper', 'N/A')}")
        print(f"Break Even Distance: ${straddle.get('break_even_distance', 'N/A')}")
        
        print("================================")