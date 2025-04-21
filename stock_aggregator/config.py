import os
import yaml
from pathlib import Path

class Config:
    """Application configuration class"""
    
    def __init__(self, config_path=None):
        """
        Initialize the Config class.
        
        Args:
            config_path (str, optional): Custom path to the config file. Useful for testing.
        """
        self.config = {}
        
        # If a custom config path is provided, use it
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
            return
            
        # Check for config file in multiple locations
        config_paths = [
            # 1. Environment variable
            os.environ.get('STOCK_AGGREGATOR_CONFIG'),
            
            # 2. Current working directory
            os.path.join(os.getcwd(), 'config.yml'),
            
            # 3. Project root directory
            self._get_project_root_config_path(),
            
            # 4. User's home directory
            str(Path.home() / '.stock_aggregator' / 'config.yml'),
            
            # 5. System-wide config (Linux/macOS)
            '/etc/stock_aggregator/config.yml'
        ]
        
        # Try each path until we find a valid config file
        for path in config_paths:
            if path and os.path.exists(path):
                self._load_config(path)
                return
                
        # If we get here, no config file was found
        raise FileNotFoundError(
            "Config file not found. Please create a config.yml file in one of the following locations:\n" +
            "\n".join([p for p in config_paths if p])
        )
    
    def _get_project_root_config_path(self):
        """Get the path to config.yml in the project root directory."""
        # Get the absolute path of the current file
        current_file = os.path.abspath(__file__)
        # Get the package directory
        package_dir = os.path.dirname(current_file)
        # Get the project root directory
        project_root = os.path.dirname(package_dir)
        # Construct the config file path
        return os.path.join(project_root, 'config.yml')
    
    def _load_config(self, config_path):
        """Load the configuration from the specified path."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"Loaded configuration from {config_path}")
        except Exception as e:
            raise ValueError(f"Error loading config from {config_path}: {str(e)}")
    
    def get_broker_connections(self, broker_type):
        """Get all connections for a specific broker type"""
        connections = []
        for connection in self.config.get('brokers', []):
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
