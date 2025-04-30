# import os
# import yaml
# from pathlib import Path

# class Config:
#     """Application configuration class"""
    
#     def __init__(self):
#         # Get the absolute path of the current file
#         current_file = os.path.abspath(__file__)
#         # Get the app directory
#         app_dir = os.path.dirname(current_file)
#         # Get the project root directory (stock-aggregator)
#         project_root = os.path.dirname(os.path.dirname(app_dir))
#         # Construct the config file path
#         config_path = os.path.join(project_root, 'config.yml')
        
#         if not os.path.exists(config_path):
#             raise FileNotFoundError(f"Config file not found at: {config_path}")
            
#         with open(config_path, 'r') as f:
#             self.config = yaml.safe_load(f)
    
#     # ... existing methods ...
    
#     # Database settings
#     @property
#     def DATABASE_URL(self):
#         """Get the PostgreSQL database URL"""
#         db_config = self.config.get('database', {})
#         return f"postgresql://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port', 5432)}/{db_config.get('name')}"
    
#     # ... rest of the class remains the same ... 