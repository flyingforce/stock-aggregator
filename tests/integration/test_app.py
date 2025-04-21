import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, MagicMock

# Mock the plaid module
import sys
sys.modules['plaid'] = MagicMock()
sys.modules['plaid.api'] = MagicMock()
sys.modules['plaid.model'] = MagicMock()
sys.modules['plaid.model.accounts_balance_get_request'] = MagicMock()
sys.modules['plaid.model.accounts_get_request'] = MagicMock()
sys.modules['plaid.model.item_public_token_exchange_request'] = MagicMock()
sys.modules['plaid.model.link_token_create_request'] = MagicMock()
sys.modules['plaid.model.link_token_create_request_user'] = MagicMock()

from stock_aggregator.main import app
from stock_aggregator.config import Config

class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'config.yml')
        
        # Sample config data with mock brokers
        self.config_data = {
            'brokers': [
                {
                    'type': 'schwab',
                    'id': 'test_schwab',
                    'enabled': True,
                    'use_mock': True,
                    'credentials': {
                        'client_id': 'test_client_id',
                        'client_secret': 'test_client_secret',
                        'refresh_token': 'test_refresh_token',
                        'redirect_uri': 'https://test.com/callback'
                    }
                }
            ],
            'redis': {
                'url': 'redis://localhost:6379/0'
            },
            'app': {
                'port': 5001,
                'debug': True
            }
        }
        
        # Write the config to the temporary file
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config_data, f)
        
        # Set environment variable to use our test config
        os.environ['STOCK_AGGREGATOR_CONFIG'] = self.config_path
        
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True
    
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
        # Remove environment variable
        if 'STOCK_AGGREGATOR_CONFIG' in os.environ:
            del os.environ['STOCK_AGGREGATOR_CONFIG']
    
    @patch('stock_aggregator.services.brokers_data.BrokersDataService.get_positions')
    @patch('stock_aggregator.services.brokers_data.BrokersDataService.get_accounts')
    def test_index_route(self, mock_get_accounts, mock_get_positions):
        """Test the index route returns 200 status code"""
        # Mock the broker data service methods
        mock_get_positions.return_value = {
            'positions_by_type': {
                'equity': [],
                'option': [],
                'collective_investment': [],
                'fixed_income': [],
                'other': [],
                'cash': []
            },
            'totals': {
                'equity': {'market_value': 0.0, 'unrealized_pl': 0.0},
                'option': {'market_value': 0.0, 'unrealized_pl': 0.0},
                'collective_investment': {'market_value': 0.0, 'unrealized_pl': 0.0},
                'fixed_income': {'market_value': 0.0, 'unrealized_pl': 0.0},
                'other': {'market_value': 0.0, 'unrealized_pl': 0.0},
                'cash': {'market_value': 0.0, 'unrealized_pl': 0.0}
            },
            'total_market_value': 0.0,
            'total_unrealized_pl': 0.0
        }
        mock_get_accounts.return_value = []
        
        # Test the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
