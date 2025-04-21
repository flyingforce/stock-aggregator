import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = timedelta(minutes=5)

    def _parse_option_symbol(self, symbol: str) -> Optional[Dict]:
        """Parse an options symbol into its components."""
        # Remove extra spaces and clean up the symbol
        symbol = ' '.join(symbol.split())
        
        # Try to match pattern like "SPY   250829C00585000" (with multiple spaces)
        match = re.match(r'^([A-Z]+)\s*(\d{6})([CP])(\d{8})$', symbol)
        if not match:
            return None
            
        underlying, expiration, option_type, strike = match.groups()
        
        # Convert expiration from YYMMDD to YYYY-MM-DD
        year = '20' + expiration[:2]
        month = expiration[2:4]
        day = expiration[4:6]
        expiration_date = f"{year}-{month}-{day}"
        
        # Convert strike price from cents to dollars
        strike_price = float(strike) / 1000.0
        
        return {
            'underlying': underlying,
            'expiration': expiration_date,
            'option_type': 'call' if option_type == 'C' else 'put',
            'strike': strike_price
        }

    def _get_option_price(self, symbol: str) -> float:
        """Get the current price for an options symbol."""
        option_data = self._parse_option_symbol(symbol)
        if not option_data:
            return 0.0
            
        try:
            # Get the underlying stock's option chain
            ticker = yf.Ticker(option_data['underlying'])
            options = ticker.option_chain(option_data['expiration'])
            
            # Get the appropriate chain (calls or puts)
            chain = options.calls if option_data['option_type'] == 'call' else options.puts
            
            # Find the matching strike price
            matching_option = chain[chain['strike'] == option_data['strike']]
            if not matching_option.empty:
                return float(matching_option['lastPrice'].iloc[0])
                
            return 0.0
        except Exception as e:
            logger.debug(f"Error getting option price for {symbol}: {str(e)}")
            return 0.0

    def _is_fixed_income(self, symbol: str) -> bool:
        """Check if the symbol is a fixed income security (CUSIP)."""
        # CUSIP pattern: 
        # First 4 characters must be numbers
        # Middle characters can be alphanumeric
        # Last character must be a number
        if len(symbol) < 5:  # Must be at least 5 characters
            return False
            
        # Check first 4 characters are numbers
        if not symbol[:4].isdigit():
            return False
            
        # Check last character is a number
        if not symbol[-1].isdigit():
            return False
            
        # Check middle characters are alphanumeric
        middle = symbol[4:-1]
        if not middle.isalnum():
            return False
            
        return True

    def get_stock_info(self, symbol: str) -> Dict:
        """Get comprehensive stock information including name and current price."""
        # Check if this is a fixed income security first
        if self._is_fixed_income(symbol):
            return {
                'name': symbol,  # Use CUSIP as name
                'current_price': 0.0,  # Price will come from broker data
                'sector': 'Fixed Income',
                'industry': 'Fixed Income'
            }
        
        # print(f"Checking if {symbol} is not a fixed income security")

        # Check if this is an options symbol
        option_data = self._parse_option_symbol(symbol)
        if option_data:
            current_price = self._get_option_price(symbol)
            return {
                'name': f"{option_data['underlying']} {option_data['expiration']} {option_data['option_type'].upper()} {option_data['strike']}",
                'current_price': current_price,
                'sector': 'Options',
                'industry': 'Options'
            }

        # Check cache for regular stocks
        now = datetime.now()
        if symbol in self._cache:
            cached_data = self._cache[symbol]
            if now - cached_data['timestamp'] < self._cache_timeout:
                return cached_data['info']

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            stock_info = {
                'name': info.get('longName', symbol),
                'current_price': info.get('regularMarketPrice', 0.0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', '')
            }
            
            self._cache[symbol] = {
                'info': stock_info,
                'timestamp': now
            }
            return stock_info
        except Exception as e:
            # Silently return default values for 404 errors
            if "404" in str(e):
                return {
                    'name': symbol,
                    'current_price': 0.0,
                    'sector': '',
                    'industry': ''
                }
            # Log other errors but still return default values
            logger.debug(f"Error getting info for {symbol}: {str(e)}")
            return {
                'name': symbol,
                'current_price': 0.0,
                'sector': '',
                'industry': ''
            }

    def get_current_price(self, symbol: str) -> float:
        """Get the current price for a symbol."""
        return self.get_stock_info(symbol)['current_price']

    def get_option_chain(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """Get option chain data for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            if expiration:
                options = ticker.option_chain(expiration)
            else:
                options = ticker.option_chain()
            
            return {
                'calls': options.calls.to_dict('records'),
                'puts': options.puts.to_dict('records')
            }
        except Exception as e:
            # Silently return empty option chain for 404 errors
            if "404" in str(e):
                return {'calls': [], 'puts': []}
            # Log other errors but still return empty option chain
            logger.debug(f"Error getting option chain for {symbol}: {str(e)}")
            return {'calls': [], 'puts': []} 