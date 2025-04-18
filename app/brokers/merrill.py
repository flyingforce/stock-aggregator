import plaid
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from typing import List, Dict, Any
from .base import Broker
from ..config import Config
import logging

logger = logging.getLogger(__name__)

class MerrillBroker(Broker):
    def __init__(self, connection_id=None):
        super().__init__()
        self.config = Config()
        self.connection_id = connection_id
        self.connection = self.config.get_broker_connection(connection_id)
        self.credentials = self.config.get_broker_credentials('merrill', connection_id)
        self.use_mock = self.credentials.get('use_mock', False)
        
        # Initialize Plaid client
        if not self.use_mock:
            configuration = plaid.Configuration(
                host=plaid.Environment.Sandbox if self.credentials.get('sandbox', True) else plaid.Environment.Development,
                api_key={
                    'clientId': self.credentials.get('client_id'),
                    'secret': self.credentials.get('secret'),
                    'plaidVersion': '2020-09-14'
                }
            )
            api_client = plaid.ApiClient(configuration)
            self.client = plaid_api.PlaidApi(api_client)
            self.access_token = self.credentials.get('access_token')

    def is_enabled(self):
        """Check if the specific Merrill connection is enabled"""
        return self.config.is_broker_enabled(self.connection_id)

    def get_accounts(self) -> List[Dict]:
        """Get all accounts for Merrill through Plaid."""
        if not self.is_enabled():
            return []
            
        if self.use_mock:
            return self._generate_mock_accounts()
            
        try:
            request = AccountsGetRequest(access_token=self.access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response.accounts:
                if account.type == 'investment':
                    accounts.append({
                        'id': account.account_id,
                        'name': account.name,
                        'type': account.subtype,
                        'status': 'ACTIVE',
                        'balance': account.balances.current,
                        'connection_id': self.connection_id
                    })
            return accounts
        except Exception as e:
            logger.error(f"Error getting Merrill accounts: {str(e)}")
            return []

    def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for a specific Merrill account through Plaid."""
        if not self.is_enabled():
            return []
            
        if self.use_mock:
            return self._generate_mock_positions()
            
        try:
            request = AccountsBalanceGetRequest(access_token=self.access_token)
            response = self.client.accounts_balance_get(request)
            
            positions = []
            for account in response.accounts:
                if account.account_id == account_id and account.type == 'investment':
                    for security in account.securities:
                        positions.append({
                            'symbol': security.ticker_symbol,
                            'name': security.name,
                            'quantity': security.quantity,
                            'average_price': security.cost_basis,
                            'current_price': security.current_price,
                            'market_value': security.current_price * security.quantity,
                            'unrealized_pl': (security.current_price - security.cost_basis) * security.quantity,
                            'asset_type': self._get_asset_type(security.type),
                            'connection_id': self.connection_id,
                            'account_id': account_id
                        })
            return positions
        except Exception as e:
            logger.error(f"Error getting Merrill positions: {str(e)}")
            return []
    
    def get_all_positions(self) -> Dict[str, List[Dict]]:
        """Get all positions for Merrill through Plaid."""
        if not self.is_enabled():
            return {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }
            
        if self.use_mock:
            mock_positions = self._generate_mock_positions()
            return {
                'equity': mock_positions,
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }
            
        try:
            positions_by_type = {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }
            
            # Get all accounts
            accounts = self.get_accounts()
            for account in accounts:
                # Get positions for each account
                positions = self.get_positions(account['id'])
                for position in positions:
                    asset_type = position.get('asset_type', 'other')
                    positions_by_type[asset_type].append(position)
                
                # Add cash position
                if 'balance' in account:
                    positions_by_type['cash'].append({
                        'symbol': 'CASH',
                        'name': 'Cash',
                        'quantity': account['balance'],
                        'average_price': 1.0,
                        'current_price': 1.0,
                        'market_value': account['balance'],
                        'unrealized_pl': 0.0,
                        'unrealized_pl_percent': 0.0,
                        'accounts': [{
                            'account_id': account['id'],
                            'quantity': account['balance'],
                            'average_price': 1.0,
                            'market_value': account['balance'],
                            'unrealized_pl': 0.0
                        }]
                    })
            
            return positions_by_type
        except Exception as e:
            logger.error(f"Error getting Merrill positions: {str(e)}")
            return {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }

    def _get_asset_type(self, security_type: str) -> str:
        """Convert Plaid security type to our asset type."""
        type_mapping = {
            'equity': 'equity',
            'etf': 'collective_investment',
            'mutual fund': 'collective_investment',
            'fixed income': 'fixed_income',
            'option': 'option'
        }
        return type_mapping.get(security_type.lower(), 'other')

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
                'name': f'{symbol} Common Stock',
                'quantity': quantity,
                'average_price': cost_basis,
                'current_price': current_price,
                'market_value': quantity * current_price,
                'unrealized_pl': (current_price - cost_basis) * quantity,
                'asset_type': 'equity',
                'connection_id': self.connection_id,
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
                'id': f'mock-account-{i+1}',
                'name': f'Merrill {account_types[i]} Account',
                'type': account_types[i],
                'status': 'ACTIVE',
                'balance': 40000.00 * (i + 1),
                'connection_id': self.connection_id
            }
            accounts.append(account)
        
        return accounts 