from typing import List, Dict
from .base import Broker

class MerrillBroker(Broker):
    def __init__(self):
        super().__init__()
        self.use_mock = False  # For now, use mock data until real API implementation

    def get_accounts(self) -> List[Dict]:
        """Get all accounts for Merrill."""
        if self.use_mock:
            return self._generate_mock_accounts()
        # TODO: Implement real account fetching
        return []

    def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for a specific Merrill account."""
        if self.use_mock:
            return self._generate_mock_positions()
        # TODO: Implement real position fetching
        return []
    
    def get_all_positions(self) -> List[Dict]:
        """Get all positions for Merrill."""
        return []

    def _generate_mock_positions(self) -> List[Dict]:
        """Generate mock position data for demonstration"""
        positions = []
        symbols = ['IBM', 'ORCL', 'CSCO', 'INTC', 'QCOM', 'TXN', 'ADBE', 'CRM', 'AVGO', 'AMD']
        
        for symbol in symbols:
            quantity = round(50 * (1 + 0.5 * (hash(symbol) % 10) / 10), 2)  # Random quantity between 50-75
            current_price = self.market_data.get_current_price(symbol)
            cost_basis = current_price * (1 - 0.1 * (hash(symbol) % 10) / 10)  # Random cost basis 0-10% below current
            
            position = {
                'symbol': symbol,
                'description': f'{symbol} Common Stock',
                'quantity': quantity,
                'cost_basis_price': cost_basis,
                'account_id': 'mock-account-1'
            }
            positions.append(position)
        
        return positions

    def _generate_mock_accounts(self) -> List[Dict]:
        """Generate mock account data for demonstration"""
        accounts = []
        account_types = ['Individual', 'Joint', 'IRA', 'Roth IRA']
        
        for i in range(4):
            account = {
                'account_id': f'mock-account-{i+1}',
                'account_name': f'Merrill {account_types[i]} Account',
                'account_number': f'****{i+1}567',
                'account_type': account_types[i],
                'balance': 40000.00 * (i + 1)
            }
            accounts.append(account)
        
        return accounts 