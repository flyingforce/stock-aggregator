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

    

    def get_option_chain(self, symbol: str, expiration: str = None) -> Dict:
        """Get option chain data for a symbol."""
        return self.market_data.get_option_chain(symbol, expiration) 