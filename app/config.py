import os
import yaml
from pathlib import Path

class Config:
    """Application configuration class"""
    
    def __init__(self):
        # Get the absolute path of the current file
        current_file = os.path.abspath(__file__)
        # Get the app directory
        app_dir = os.path.dirname(current_file)
        # Get the project root directory (stock-aggregator)
        project_root = os.path.dirname(app_dir)
        # Construct the config file path
        config_path = os.path.join(project_root, 'config.yml')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get_broker_connections(self, broker_type):
        """Get all connections for a specific broker type"""
        connections = []
        for connection in self.config.get('brokers', []):
            print(f"config connection: {connection}")
            if connection.get('type') == broker_type:
                connections.append(connection)
        return connections
    
    def get_broker_connection(self, connection_id):
        """Get a specific broker connection by its ID"""
        for connection in self.config.get('brokers', []):
            if connection.get('id') == connection_id:
                return connection
        return None
    
    def is_broker_enabled(self, connection_id):
        """Check if a specific broker connection is enabled"""
        connection = self.get_broker_connection(connection_id)
        if not connection:
            return False
        return connection.get('enabled', False)
    
    def should_use_mock(self, broker_type, connection_id=None):
        """Check if mock data should be used for a broker connection"""
        if connection_id:
            connection = self.get_broker_connection(connection_id)
            if connection:
                return connection.get('use_mock', False)
            return False
        else:
            connections = self.get_broker_connections(broker_type)
            for conn in connections:
                if conn.get('enabled', False):
                    return conn.get('use_mock', False)
            return False
    
    def get_broker_credentials(self, broker_type, connection_id=None):
        """Get credentials for a specific broker connection"""
        if connection_id:
            connection = self.get_broker_connection(connection_id)
            if connection:
                return {
                    'client_id': connection.get('credentials', {}).get('client_id'),
                    'client_secret': connection.get('credentials', {}).get('client_secret'),
                    'refresh_token': connection.get('credentials', {}).get('refresh_token'),
                    'redirect_uri': connection.get('credentials', {}).get('redirect_uri'),
                    'use_mock': connection.get('use_mock', False)
                }
            return {}
        else:
            connections = self.get_broker_connections(broker_type)
            for conn in connections:
                if conn.get('enabled', False):
                    return {
                        'client_id': conn.get('credentials', {}).get('client_id'),
                        'client_secret': conn.get('credentials', {}).get('client_secret'),
                        'refresh_token': conn.get('credentials', {}).get('refresh_token'),
                        'redirect_uri': conn.get('credentials', {}).get('redirect_uri'),
                        'use_mock': conn.get('use_mock', False)
                    }
            return {}

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Redis settings
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Broker settings
    BROKER_CONFIG_PATH = os.environ.get('BROKER_CONFIG_PATH', 
                                       str(Path.home() / '.stock_aggregator' / 'config.yml'))
    
    # Template settings
    TEMPLATES_AUTO_RELOAD = True 