from flask import Flask, render_template
from .config import Config
from datetime import datetime
from .brokers.schwab import SchwabBroker
from .brokers.merrill import MerrillBroker

app = Flask(__name__)
app.config.from_object(Config)

# Initialize config
config = Config()

@app.route('/')
def index():
    # Initialize empty data structures
    combined_positions = {
        'equity': [],
        'option': [],
        'collective_investment': [],
        'fixed_income': [],
        'other': []
    }
    
    combined_totals = {
        'equity': {'market_value': 0.0, 'unrealized_pl': 0.0},
        'option': {'market_value': 0.0, 'unrealized_pl': 0.0},
        'collective_investment': {'market_value': 0.0, 'unrealized_pl': 0.0},
        'fixed_income': {'market_value': 0.0, 'unrealized_pl': 0.0},
        'other': {'market_value': 0.0, 'unrealized_pl': 0.0}
    }
    
    total_market_value = 0.0
    total_unrealized_pl = 0.0
    all_accounts = []
    
    # Process Schwab positions if any connection is enabled
    # if config.is_broker_enabled('schwab'):
    # Get all Schwab connections
    schwab_connections = config.get_broker_connections('schwab')
    for connection in schwab_connections:
        print(f"connection: {connection}")
        if connection.get('enabled', False):
            # Initialize broker with specific connection
            schwab_broker = SchwabBroker(connection.get('id'))
            schwab_data = schwab_broker.combine_all_positions()
            print(f"schwab_data: {schwab_data}")
            
            # Combine positions
            for asset_type in combined_positions:
                combined_positions[asset_type].extend(schwab_data['positions'][asset_type])
            
            # Combine totals
            for asset_type in combined_totals:
                combined_totals[asset_type]['market_value'] += schwab_data['totals'][asset_type]['market_value']
                combined_totals[asset_type]['unrealized_pl'] += schwab_data['totals'][asset_type]['unrealized_pl']
            
            # Update overall totals
            total_market_value += schwab_data['total_market_value']
            total_unrealized_pl += schwab_data['total_unrealized_pl']
            
            # Add accounts
            all_accounts.extend(schwab_broker.get_accounts())
    
    # Process Merrill positions if any connection is enabled
    # if config.is_broker_enabled('merrill'):
    # Get all Merrill connections
    merrill_connections = config.get_broker_connections('merrill')
    for connection in merrill_connections:
        if connection.get('enabled', False):
            # Initialize broker with specific connection
            merrill_broker = MerrillBroker(connection.get('id'))
            merrill_data = merrill_broker.get_all_positions()
            
            # Combine positions
            for asset_type in combined_positions:
                combined_positions[asset_type].extend(merrill_data['positions'][asset_type])
            
            # Combine totals
            for asset_type in combined_totals:
                combined_totals[asset_type]['market_value'] += merrill_data['totals'][asset_type]['market_value']
                combined_totals[asset_type]['unrealized_pl'] += merrill_data['totals'][asset_type]['unrealized_pl']
            
            # Update overall totals
            total_market_value += merrill_data['total_market_value']
            total_unrealized_pl += merrill_data['total_unrealized_pl']
            
            # Add accounts
            all_accounts.extend(merrill_broker.get_accounts())
    
    # Get last updated time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html',
                         positions=combined_positions,
                         totals=combined_totals,
                         total_market_value=total_market_value,
                         total_unrealized_pl=total_unrealized_pl,
                         accounts=all_accounts,
                         last_updated=last_updated)

if __name__ == '__main__':
    app.run(debug=True) 