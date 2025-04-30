from flask import render_template, jsonify
from datetime import datetime, date
from ..services.brokers_data import BrokersDataService
from ..db.repository import Repository
from ..config import Config

def init_routes(app):
    config = Config()
    repository = Repository(config.DATABASE_URL)
    brokers_data = BrokersDataService()
    
    @app.route('/')
    def index():
        # Get current positions
        positions_data = brokers_data.get_positions()
        
        # Get available dates from database
        available_dates = repository.get_available_dates()
        
        return render_template('index.html',
                             positions=positions_data['positions_by_type'],
                             totals=positions_data['totals'],
                             total_market_value=positions_data['total_market_value'],
                             total_cash=positions_data['total_cash'],
                             total_unrealized_pl=positions_data['total_unrealized_pl'],
                             accounts=positions_data.get('accounts', []),
                             last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             available_dates=[d.strftime('%Y-%m-%d') for d in available_dates])
    
    @app.route('/portfolio/<date_str>')
    def portfolio_by_date(date_str):
        try:
            # Parse the date string
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Get account snapshot for the selected date
            account_snapshot = repository.get_account_snapshot(selected_date)
            if not account_snapshot:
                return render_template('error.html', message='No data available for this date'), 404
            
            # Get position snapshot for the selected date
            position_snapshot = repository.get_position_snapshot(selected_date)
            if not position_snapshot:
                return render_template('error.html', message='No position data available for this date'), 404
            
            # Get available dates for the calendar
            available_dates = repository.get_available_dates()
            
            return render_template('index.html',
                                 positions=position_snapshot.position_info['positions_by_type'],
                                 totals=position_snapshot.position_info['totals'],
                                 total_market_value=position_snapshot.market_value,
                                 total_cash=account_snapshot.cash_total,
                                 total_unrealized_pl=position_snapshot.open_pl,
                                 accounts=account_snapshot.account_info['accounts'],
                                 last_updated=selected_date.strftime('%Y-%m-%d'),
                                 selected_date=selected_date.strftime('%Y-%m-%d'),
                                 available_dates=[d.strftime('%Y-%m-%d') for d in available_dates])
        
        except ValueError:
            return render_template('error.html', message='Invalid date format'), 400
    
    @app.route('/api/available-dates')
    def get_available_dates():
        available_dates = repository.get_available_dates()
        return jsonify([d.strftime('%Y-%m-%d') for d in available_dates]) 