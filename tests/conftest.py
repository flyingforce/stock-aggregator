import pytest
import os
import tempfile
import yaml
import shutil

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.yml')
    
    # Sample config data
    config_data = {
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
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    
    yield config_path
    
    # Clean up the temporary directory
    shutil.rmtree(temp_dir)
