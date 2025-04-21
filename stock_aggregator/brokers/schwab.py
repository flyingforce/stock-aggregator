import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import Broker
from ..config import Config
import base64
import logging

logger = logging.getLogger(__name__)

class SchwabBroker(Broker):
    def __init__(self, connection_id=None):
        super().__init__()
        self.config = Config()
        self.connection_id = connection_id
        self.connection = self.config.get_broker_connection(connection_id)
        self.credentials = self.config.get_broker_credentials('schwab', connection_id)
        self.base_url = 'https://api.schwabapi.com/trader/v1'
        self.token_url ='https://api.schwabapi.com/v1/oauth/token'
        self.access_token = None
        self.refresh_token = self.credentials.get('refresh_token')
        self.token_expires_at = None
        self.logger = logging.getLogger(__name__)
        self.broker_name = "Charles Schwab"
        self.use_mock = self.credentials.get('use_mock', False)
        
        # Validate required credentials
        if not self.use_mock:
            required_fields = ['client_id', 'client_secret', 'refresh_token']
            missing_fields = [field for field in required_fields if not self.credentials.get(field)]
            if missing_fields:
                self.logger.error(f"Missing required credentials: {', '.join(missing_fields)}")
                self.use_mock = True
                self.logger.warning("Falling back to mock data mode")

    def is_enabled(self):
        """Check if the specific Schwab connection is enabled"""
        return self.config.is_broker_enabled(self.connection_id)
    
    def get_access_token(self):
        """Get or refresh access token using refresh token"""
        if self.use_mock:
            return "mock_access_token"
            
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        try:
            # Create Basic Auth header
            print(f"client_id: {self.credentials['client_id']} client_secret: {self.credentials['client_secret']}")
            print(f"refresh_token: {self.refresh_token}")
            auth_string = f"{self.credentials['client_id']}:{self.credentials['client_secret']}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            response = requests.post(
                f"{self.token_url}",
                headers={
                    'Authorization': f'Basic {encoded_auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token
                }
            )
            response.raise_for_status()
            token_data = response.json()
            
            # Update tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token', self.refresh_token)  # Keep existing if not provided
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
            
            return self.access_token
        except Exception as e:
            self.logger.error(f"Error getting access token: {str(e)}")
            raise

    def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for a specific account."""
        return []
    
    def get_all_positions(self) -> Dict[str, List[Dict]]:
        """Get all positions from Schwab API"""
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
                'other': []
            }
            
        try:
            access_token = self.get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            print(f"request url: {f'{self.base_url}/accounts/?fields=positions'} token: {access_token}")
            response = requests.get(
                f"{self.base_url}/accounts?fields=positions",
                headers=headers
            )
            response.raise_for_status()
            
            accounts_data = response.json()
            positions_by_type = {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }
            
            for account in accounts_data:
                if 'securitiesAccount' in account and 'positions' in account['securitiesAccount']:
                    for position in account['securitiesAccount']['positions']:
                        instrument = position['instrument']
                        
                        # Calculate quantity (long - short)
                        quantity = position['longQuantity'] - position['shortQuantity']
                        if quantity == 0:
                            continue
                            
                        # Multiply quantity by 10 for Fixed Income assets
                        if instrument['assetType'] == 'FIXED_INCOME':
                            quantity *= 10
                            
                        # Use averagePrice as cost basis
                        cost_basis_price = position.get('averagePrice', 0)
                        if cost_basis_price == 0:
                            cost_basis_price = position.get('averageLongPrice', 0)
                            
                        position_data = {
                            'symbol': instrument['symbol'],
                            'name': instrument.get('description', ''),
                            'quantity': quantity,
                            'average_price': cost_basis_price,
                            'current_price': position['marketValue'] / quantity if quantity != 0 else 0,
                            'market_value': position['marketValue'],
                            'unrealized_pl': position.get('unrealizedGainLoss', 0),
                            'asset_type': instrument['assetType'],
                            'connection_id': self.connection_id,
                            'account_id': account['securitiesAccount']['accountNumber']
                        }   
                        
                        # Add to appropriate asset type list
                        asset_type = instrument['assetType'].lower()
                        if asset_type == 'equity':
                            positions_by_type['equity'].append(position_data)
                        elif asset_type == 'option':
                            positions_by_type['option'].append(position_data)
                        elif asset_type in ['mutual_fund', 'etf', 'collective_investment']:
                            positions_by_type['collective_investment'].append(position_data)
                        elif asset_type == 'fixed_income':
                            positions_by_type['fixed_income'].append(position_data)
                        else:
                            positions_by_type['other'].append(position_data)
                    positions_by_type['cash'].append({
                        'symbol': 'CASH',
                        'name': 'Cash',
                        'quantity': account['securitiesAccount']['currentBalances']['cashBalance'],
                        'average_price': 1.0,
                        'current_price': 1.0,
                        'market_value': account['securitiesAccount']['currentBalances']['cashBalance'],
                        'unrealized_pl': 0.0,
                        'unrealized_pl_percent': 0.0,
                        'accounts': [{
                            'account_id': account['securitiesAccount']['accountNumber'],
                            'quantity': account['securitiesAccount']['currentBalances']['cashBalance'],
                            'average_price': 1.0,
                            'market_value': account['securitiesAccount']['currentBalances']['cashBalance'],
                            'unrealized_pl': 0.0
                        }]
                    })
            
            return positions_by_type
        except Exception as e:
            self.logger.error(f"Error getting positions: {str(e)}")
            return {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            }
    
    def get_accounts(self):
        """Get accounts from Schwab API"""
        if not self.is_enabled():
            return []
            
        if self.use_mock:
            return self._generate_mock_accounts()
            
        try:
            access_token = self.get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/accounts",
                headers=headers
            )
            response.raise_for_status()
            
            accounts_data = response.json()
            accounts = []
            
            for account in accounts_data:
                if 'securitiesAccount' in account:
                    securities_account = account['securitiesAccount']
                    current_balances = securities_account.get('currentBalances', {})
                    
                    accounts.append({
                        'id': securities_account['accountNumber'],
                        'name': f"Schwab {securities_account['type']} Account",
                        'type': securities_account['type'],
                        'status': securities_account.get('status', 'ACTIVE'),
                        'balance': current_balances.get('liquidationValue', 0),
                        'connection_id': self.connection_id
                    })
            
            return accounts
        except Exception as e:
            self.logger.error(f"Error getting accounts: {str(e)}")
            return []

    def get_token(self, auth_code: str = None) -> Dict[str, Any]:
        """Get access token using refresh token or authorization code."""
        try:
            # Create Basic Auth header with client ID and secret
            auth_string = f"{self.credentials['client_id']}:{self.credentials['client_secret']}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            auth_header = f"Basic {encoded_auth}"

            # Prepare request data
            data = {
                'grant_type': 'refresh_token' if not auth_code else 'authorization_code',
                'client_id': self.credentials['client_id'],
                'client_secret': self.credentials['client_secret']
            }

            # Add refresh token or auth code based on grant type
            if auth_code:
                data.update({
                    'code': auth_code,
                    'redirect_uri': self.credentials.get('redirect_uri')
                })
            else:
                data['refresh_token'] = self.refresh_token

            # Make request to Schwab API
            response = requests.post(
                'https://api.schwabapi.com/v1/oauth/token',
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data=data
            )
            response.raise_for_status()
            token_data = response.json()

            # Update instance variables with new tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting token: {str(e)}")
            raise

    def _generate_mock_positions(self) -> List[Dict]:
        """Generate mock position data for demonstration"""
        positions = []
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT']
        
        for symbol in symbols:
            quantity = round(100 * (1 + 0.5 * (hash(symbol) % 10) / 10), 2)  # Random quantity between 100-150
            current_price = self.market_data.get_current_price(symbol)
            cost_basis_price = current_price * (1 - 0.1 * (hash(symbol) % 10) / 10)  # Random cost basis 0-10% below current
            
            position = {
                'symbol': symbol,
                'description': f'{symbol} Common Stock',
                'quantity': quantity,
                'cost_basis_price': cost_basis_price,
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
                'account_name': f'Schwab {account_types[i]} Account',
                'account_number': f'****{i+1}234',
                'account_type': account_types[i],
                'balance': 50000.00 * (i + 1)
            }
            accounts.append(account)
        
        return accounts 