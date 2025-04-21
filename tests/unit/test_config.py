import unittest
import os
import tempfile
import yaml
from stock_aggregator.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'config.yml')
        
        # Sample config data
        self.config_data = {
            'brokers': [
                {
                    'type': 'test_broker',
                    'id': 'test1',
                    'enabled': True,
                    'use_mock': True,
                    'credentials': {
                        'client_id': 'test_client_id',
                        'client_secret': 'test_client_secret',
                        'refresh_token': 'test_refresh_token',
                        'redirect_uri': 'https://test.com/callback'
                    }
                },
                {
                    'type': 'test_broker',
                    'id': 'test2',
                    'enabled': False,
                    'use_mock': True,
                    'credentials': {
                        'client_id': 'test_client_id_2',
                        'client_secret': 'test_client_secret_2',
                        'refresh_token': 'test_refresh_token_2',
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
    
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_config_loading(self):
        """Test that config is loaded correctly"""
        config = Config(config_path=self.config_path)
        self.assertIsNotNone(config.config)
        self.assertEqual(config.config['app']['port'], 5001)
        self.assertEqual(config.config['app']['debug'], True)
        self.assertEqual(len(config.config['brokers']), 2)
    
    def test_get_broker_connections(self):
        """Test getting broker connections by type"""
        config = Config(config_path=self.config_path)
        connections = config.get_broker_connections('test_broker')
        self.assertEqual(len(connections), 2)
        self.assertEqual(connections[0]['id'], 'test1')
        self.assertEqual(connections[1]['id'], 'test2')
    
    def test_get_broker_connection(self):
        """Test getting a specific broker connection by ID"""
        config = Config(config_path=self.config_path)
        connection = config.get_broker_connection('test1')
        self.assertIsNotNone(connection)
        self.assertEqual(connection['type'], 'test_broker')
        self.assertEqual(connection['enabled'], True)
        
        # Test non-existent connection
        connection = config.get_broker_connection('non_existent')
        self.assertIsNone(connection)
    
    def test_is_broker_enabled(self):
        """Test checking if a broker connection is enabled"""
        config = Config(config_path=self.config_path)
        self.assertTrue(config.is_broker_enabled('test1'))
        self.assertFalse(config.is_broker_enabled('test2'))
        self.assertFalse(config.is_broker_enabled('non_existent'))

if __name__ == '__main__':
    unittest.main()
