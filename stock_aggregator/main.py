from flask import Flask, render_template
from .config import Config
from datetime import datetime
from .services.brokers_data import BrokersDataService

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
brokers_data = BrokersDataService()

# Custom filter for formatting dollar amounts
@app.template_filter('formatDollar')
def format_dollar(value):
    if value is None:
        return '$0.00'
    return '${:,.2f}'.format(float(value))

@app.route('/')
def index():
    # Get all data from brokers
    positions_data = brokers_data.get_positions()
    accounts = brokers_data.get_accounts()
    
    # Get last updated time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('index.html',
                         positions=positions_data['positions_by_type'],
                         totals=positions_data['totals'],
                         total_market_value=positions_data['total_market_value'],
                         total_unrealized_pl=positions_data['total_unrealized_pl'],
                         accounts=accounts,
                         last_updated=last_updated)

if __name__ == '__main__':
    app.run(debug=True) 