from abc import ABC, abstractmethod
from typing import List, Dict
from ..services.market_data import MarketDataService

class Broker(ABC):
    def __init__(self):
        self.market_data = MarketDataService()

    @abstractmethod
    def get_accounts(self) -> List[Dict]:
        """Get all accounts for this broker."""
        pass

    @abstractmethod
    def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for a specific account."""
        pass

    @abstractmethod
    def get_all_positions(self) -> Dict[str, List[Dict]]:
        """Get all positions grouped by asset type."""
        pass

    def combine_all_positions(self) -> Dict:
        """Get all positions across all accounts with current market data."""
        positions_by_type = {
            'equity': [],
            'option': [],
            'collective_investment': [],
            'fixed_income': [],
            'other': []
        }
        total_market_value = 0.0
        total_unrealized_pl = 0.0

        # Get all positions from all accounts
        all_positions = self.get_all_positions()
        
        # Combine positions by type
        for asset_type, positions in all_positions.items():
            positions_by_type[asset_type].extend(positions)
            
            # Calculate totals
            for position in positions:
                total_market_value += position.get('market_value', 0)
                total_unrealized_pl += position.get('unrealized_pl', 0)

        return {
            'positions_by_type': positions_by_type,
            'total_market_value': total_market_value,
            'total_unrealized_pl': total_unrealized_pl
        }

    def calculate_aggregated_position(self, positions: List[Dict]) -> Dict:
        """Calculate aggregated position data across multiple accounts."""
        if not positions:
            return {
                'symbol': '',
                'name': '',
                'total_quantity': 0.0,
                'average_cost_basis': 0.0,
                'current_price': 0.0,
                'total_market_value': 0.0,
                'total_unrealized_pl': 0.0,
                'unrealized_pl_percent': 0.0,
                'accounts': []
            }

        symbol = positions[0]['symbol']
        
        # Try to get current price from market data
        current_price = self.market_data.get_current_price(symbol)
        
        # If market data returns zero price, use the first position's current price
        if current_price <= 0:
            current_price = positions[0].get('current_price', 0)
        
        # Get stock info for name and sector
        stock_info = self.market_data.get_stock_info(symbol)
        
        total_quantity = sum(pos['quantity'] for pos in positions)
        total_cost = sum(pos['quantity'] * pos['cost_basis_price'] for pos in positions)
        
        average_cost_basis = total_cost / total_quantity if total_quantity > 0 else 0.0
        total_market_value = total_quantity * current_price
        total_unrealized_pl = total_market_value - total_cost
        unrealized_pl_percent = (total_unrealized_pl / total_cost) * 100 if total_cost > 0 else 0.0

        # Group positions by account
        account_positions = {}
        for pos in positions:
            account_id = pos['account_id']
            if account_id not in account_positions:
                account_positions[account_id] = {
                    'quantity': 0.0,
                    'cost_basis_price': 0.0,
                    'market_value': 0.0,
                    'unrealized_pl': 0.0
                }
            
            account_pos = account_positions[account_id]
            account_pos['quantity'] += pos['quantity']
            account_pos['cost_basis_price'] = pos['cost_basis_price']  # Use the position's cost basis price
            account_pos['market_value'] += pos['quantity'] * current_price
            account_pos['unrealized_pl'] = account_pos['market_value'] - (account_pos['quantity'] * account_pos['cost_basis_price'])

        return {
            'symbol': symbol,
            'name': stock_info['name'],
            'sector': stock_info['sector'],
            'industry': stock_info['industry'],
            'total_quantity': total_quantity,
            'average_cost_basis': average_cost_basis,
            'current_price': current_price,
            'total_market_value': total_market_value,
            'total_unrealized_pl': total_unrealized_pl,
            'unrealized_pl_percent': unrealized_pl_percent,
            'accounts': [
                {
                    'account_id': acc_id,
                    'quantity': pos['quantity'],
                    'average_price': pos['cost_basis_price'],  # Use cost_basis_price as average_price
                    'market_value': pos['market_value'],
                    'unrealized_pl': pos['unrealized_pl']
                }
                for acc_id, pos in account_positions.items()
            ]
        }

    def get_option_chain(self, symbol: str, expiration: str = None) -> Dict:
        """Get option chain data for a symbol."""
        return self.market_data.get_option_chain(symbol, expiration) 