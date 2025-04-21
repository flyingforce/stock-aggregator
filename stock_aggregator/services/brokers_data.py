from typing import List, Dict, Any
from datetime import date
from ..config import Config
from ..brokers.schwab import SchwabBroker
from ..brokers.merrill import MerrillBroker
from .market_data import MarketDataService
from .snapshot_service import SnapshotService
import logging

logger = logging.getLogger(__name__)

class BrokersDataService:
    def __init__(self):
        self.config = Config()
        self.brokers = {}
        self.market_data = MarketDataService()
        self.snapshot_service = SnapshotService(self.config)
        self._initialize_brokers()
    
    def _initialize_brokers(self):
        """Initialize broker instances for all enabled connections"""
        # Get all broker connections
        brokers_config = self.config.config.get('brokers', [])
        
        for broker_config in brokers_config:
            broker_type = broker_config.get('type')
            connection_id = broker_config.get('id')
            enabled = broker_config.get('enabled', False)
            
            if not enabled:
                continue
                
            if broker_type == 'schwab':
                broker = SchwabBroker(connection_id)
                if broker.is_enabled():
                    self.brokers[connection_id] = broker
            elif broker_type == 'merrill':
                broker = MerrillBroker(connection_id)
                if broker.is_enabled():
                    self.brokers[connection_id] = broker
    
    def get_accounts(self) -> List[Dict]:
        """Get all accounts from all enabled broker connections"""
        all_accounts = []
        
        for connection_id, broker in self.brokers.items():
            try:
                accounts = broker.get_accounts()
                all_accounts.extend(accounts)
            except Exception as e:
                logger.error(f"Error getting accounts from {connection_id}: {str(e)}")
        
        return all_accounts
    
    def _aggregate_positions(self, positions: List[Dict]) -> List[Dict]:
        """Aggregate positions by symbol"""
        aggregated = {}
        
        for position in positions:
            symbol = position['symbol']
            if symbol not in aggregated:
                current_price = self.market_data.get_current_price(symbol)
                if current_price <= 0:
                    current_price = position['current_price']
                aggregated[symbol] = {
                    'symbol': symbol,
                    'name': position['name'],
                    'sector': position.get('sector', ''),
                    'total_quantity': 0.0,
                    'average_cost_basis': 0.0,
                    'current_price': current_price,
                    'total_market_value': 0.0,
                    'total_unrealized_pl': 0.0,
                    'unrealized_pl_percent': 0.0,
                    'accounts': []
                }
            
            # Update aggregated position
            agg = aggregated[symbol]
            # Try to get current price from market data
            current_price = agg['current_price']
            
            # Handle fixed income positions differently
            if position.get('asset_type') == 'fixed_income':
                # For fixed income, quantity is in face value (e.g., $1000 bonds)
                # Market value is quantity * current price (as percentage of face value)
                market_value = position['quantity'] * (current_price / 100.0)
                # Cost basis is quantity * average price (as percentage of face value)
                cost_basis = position['quantity'] * (position['average_price'] / 100.0)
                unrealized_pl = market_value - cost_basis
            else:
                # For other asset types (equity, options, etc.)
                market_value = position['quantity'] * current_price
                unrealized_pl = market_value - (position['quantity'] * position['average_price'])
            
            agg['current_price'] = current_price
            agg['total_quantity'] += position['quantity']
            agg['total_market_value'] += market_value

            # Add account details
            agg['accounts'].append({
                'account_id': position.get('account_id', ''),
                'quantity': position['quantity'],
                'average_price': position['average_price'],
                'market_value': market_value,
                'total_cost': position['quantity'] * position['average_price'],
                'unrealized_pl': unrealized_pl,
            })
        
        # Calculate final values for each aggregated position
        for agg in aggregated.values():
            # Calculate total cost basis
            total_cost = sum(acc['total_cost'] for acc in agg['accounts'])
            agg['average_cost_basis'] = total_cost / agg['total_quantity'] if agg['total_quantity'] > 0 else 0
            
            # Calculate total unrealized PL
            agg['total_unrealized_pl'] = agg['total_market_value'] - total_cost
            
            # Calculate unrealized PL percentage
            if total_cost > 0:
                agg['unrealized_pl_percent'] = (agg['total_unrealized_pl'] / total_cost) * 100
        
        return list(aggregated.values())
    
    def get_positions(self) -> Dict[str, Any]:
        """Get combined positions from all enabled broker connections and store in database"""
        positions_by_type = {
            'equity': [],
            'option': [],
            'collective_investment': [],
            'fixed_income': [],
            'other': [],
            'cash': []
        }
        
        totals = {
            'equity': {'market_value': 0.0, 'unrealized_pl': 0.0},
            'option': {'market_value': 0.0, 'unrealized_pl': 0.0},
            'collective_investment': {'market_value': 0.0, 'unrealized_pl': 0.0},
            'fixed_income': {'market_value': 0.0, 'unrealized_pl': 0.0},
            'other': {'market_value': 0.0, 'unrealized_pl': 0.0},
            'cash': {'market_value': 0.0, 'unrealized_pl': 0.0}
        }
        
        total_market_value = 0.0
        total_unrealized_pl = 0.0
        total_cost_basis = 0.0
        total_cash = 0.0
        accounts = []
        
        # Get today's date for database storage
        today = date.today()
        
        for connection_id, broker in self.brokers.items():
            try:
                # Get positions from this broker
                broker_positions = broker.get_all_positions()
                
                # Combine positions by type
                for asset_type, positions in broker_positions.items():
                    positions_by_type[asset_type].extend(positions)
                    
                    # Update totals
                    if asset_type == 'cash':
                        for position in positions:
                            total_cash += position.get('market_value', 0.0)
                            accounts.append({
                                'account_id': position.get('account_id', ''),
                                'broker': broker.__class__.__name__.replace('Broker', '').lower(),
                                'cash_balance': position.get('market_value', 0.0),
                                'connection_id': connection_id
                            })
                    else:
                        for position in positions:
                            market_value = position.get('market_value', 0.0)
                            unrealized_pl = position.get('unrealized_pl', 0.0)
                            cost_basis = position.get('quantity', 0.0) * position.get('average_price', 0.0)
                            
                            totals[asset_type]['market_value'] += market_value
                            totals[asset_type]['unrealized_pl'] += unrealized_pl
                            total_market_value += market_value
                            total_unrealized_pl += unrealized_pl
                            total_cost_basis += cost_basis
                            
            except Exception as e:
                logger.error(f"Error getting positions from {connection_id}: {str(e)}")
        
        # Aggregate positions by symbol for each type
        aggregated_positions = {
            'equity': self._aggregate_positions(positions_by_type['equity']),
            'option': self._aggregate_positions(positions_by_type['option']),
            'collective_investment': self._aggregate_positions(positions_by_type['collective_investment']),
            'fixed_income': self._aggregate_positions(positions_by_type['fixed_income']),
            'other': self._aggregate_positions(positions_by_type['other']),
            'cash': positions_by_type['cash']  # Cash positions are already in the correct format
        }
        
        # Store account snapshot
        try:
            self.snapshot_service.save_account_snapshot(
                date=today,
                cash_total=total_cash,
                cost_basis=total_cost_basis,
                accounts_count=len(accounts),
                market_value=total_market_value,
                open_pl=total_unrealized_pl,
                account_info={
                    'accounts': accounts,
                    'brokers': list(self.brokers.keys()),
                    'totals': totals
                }
            )
        except Exception as e:
            logger.error(f"Error saving account snapshot: {str(e)}")
        
        # Store position snapshot
        try:
            self.snapshot_service.save_position_snapshot(
                date=today,
                cost_basis=total_cost_basis,
                market_value=total_market_value,
                open_pl=total_unrealized_pl,
                position_info={
                    'positions_by_type': aggregated_positions,
                    'totals': totals
                }
            )
        except Exception as e:
            logger.error(f"Error saving position snapshot: {str(e)}")
        
        return {
            'positions_by_type': aggregated_positions,
            'totals': totals,
            'total_market_value': total_market_value,
            'total_unrealized_pl': total_unrealized_pl
        }
    
    def get_broker(self, connection_id: str):
        """Get a specific broker instance by connection ID"""
        return self.brokers.get(connection_id)
    
    def get_enabled_connections(self) -> List[str]:
        """Get list of enabled connection IDs"""
        return list(self.brokers.keys())
    
    # def calculate_aggregated_position(self, positions: List[Dict]) -> Dict:
        """Calculate aggregated position data across multiple accounts."""
        if not positions:
            return {
                'symbol': '',
                'name': '',
                'total_quantity': 0.0,
                'average_cost_basis': 0.0,
                'current_price': 0.0,
                'total_market_value': 0.0,
                'total_unrealized_pl': 0.0,
                'unrealized_pl_percent': 0.0,
                'accounts': []
            }

        symbol = positions[0]['symbol']
        
        # Try to get current price from market data
        current_price = self.market_data.get_current_price(symbol)
        
        # If market data returns zero price, use the first position's current price
        if current_price <= 0:
            current_price = positions[0].get('current_price', 0)
        
        # Get stock info for name and sector
        stock_info = self.market_data.get_stock_info(symbol)
        
        total_quantity = sum(pos['quantity'] for pos in positions)
        total_cost = sum(pos['quantity'] * pos['cost_basis_price'] for pos in positions)
        
        average_cost_basis = total_cost / total_quantity if total_quantity > 0 else 0.0
        total_market_value = total_quantity * current_price
        total_unrealized_pl = total_market_value - total_cost
        unrealized_pl_percent = (total_unrealized_pl / total_cost) * 100 if total_cost > 0 else 0.0

        # Group positions by account
        account_positions = {}
        for pos in positions:
            account_id = pos['account_id']
            if account_id not in account_positions:
                account_positions[account_id] = {
                    'quantity': 0.0,
                    'cost_basis_price': 0.0,
                    'market_value': 0.0,
                    'unrealized_pl': 0.0
                }
            
            account_pos = account_positions[account_id]
            account_pos['quantity'] += pos['quantity']
            account_pos['cost_basis_price'] = pos['cost_basis_price']  # Use the position's cost basis price
            account_pos['market_value'] += pos['quantity'] * current_price
            account_pos['unrealized_pl'] = account_pos['market_value'] - (account_pos['quantity'] * account_pos['cost_basis_price'])

        return {
            'symbol': symbol,
            'name': stock_info['name'],
            'sector': stock_info['sector'],
            'industry': stock_info['industry'],
            'total_quantity': total_quantity,
            'average_cost_basis': average_cost_basis,
            'current_price': current_price,
            'total_market_value': total_market_value,
            'total_unrealized_pl': total_unrealized_pl,
            'unrealized_pl_percent': unrealized_pl_percent,
            'accounts': [
                {
                    'account_id': acc_id,
                    'quantity': pos['quantity'],
                    'average_price': pos['cost_basis_price'],  # Use cost_basis_price as average_price
                    'market_value': pos['market_value'],
                    'unrealized_pl': pos['unrealized_pl']
                }
                for acc_id, pos in account_positions.items()
            ]
        }