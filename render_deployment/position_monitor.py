"""
Position Monitor for $50K Strategy
Monitors ADA and SOL positions for profit-taking opportunities
"""
import time
import threading
from datetime import datetime
from models import Trade, db
from backup_data_provider import BackupDataProvider
from telegram_notifier import send_position_alert

class PositionMonitor:
    """Monitor active positions and send alerts"""
    
    def __init__(self):
        self.data_provider = BackupDataProvider()
        self.monitoring = False
        self.last_prices = {}
        
    def get_active_positions(self):
        """Get current ADA and SOL positions"""
        positions = []
        
        # ADA SHORT position
        positions.append({
            'symbol': 'ADA',
            'side': 'SHORT',
            'entry_price': 0.591,
            'quantity': 145.28,
            'leverage': 18,
            'stop_loss': 0.611,
            'take_profit_50': 0.575,
            'take_profit_100': 0.558
        })
        
        # SOL SHORT position  
        positions.append({
            'symbol': 'SOL',
            'side': 'SHORT',
            'entry_price': 144.05,
            'quantity': 1.04,
            'leverage': 20,
            'stop_loss': 148.37,
            'take_profit_50': 139.73,
            'take_profit_100': 135.41
        })
        
        return positions
    
    def check_profit_targets_and_stops(self, positions, current_prices):
        """Check if any positions hit profit targets or stop losses"""
        for position in positions:
            symbol = position['symbol']
            if symbol not in current_prices:
                continue
                
            current_price = current_prices[symbol]['price']
            entry_price = position['entry_price']
            stop_loss = position['stop_loss']
            
            # Calculate current P&L percentage
            if position['side'] == 'SHORT':
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
                loss_amount = (current_price - entry_price) * position['quantity']
            else:
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                loss_amount = (entry_price - current_price) * position['quantity']
            
            # Check for stop loss first (most critical)
            if (position['side'] == 'SHORT' and current_price >= stop_loss) or \
               (position['side'] == 'LONG' and current_price <= stop_loss):
                details = {
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'loss_amount': abs(loss_amount),
                    'pnl_percent': pnl_percent,
                    'side': position['side'],
                    'leverage': position['leverage']
                }
                send_position_alert("STOP_LOSS", symbol, details)
                print(f"STOP LOSS alert sent for {symbol}")
                continue  # Skip profit checks if stop loss hit
            
            # Check for 50% profit target
            if current_price <= position['take_profit_50'] and position['side'] == 'SHORT':
                profit_amount = (entry_price - current_price) * position['quantity'] * 0.5
                details = {
                    'percentage': 50,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'profit': profit_amount
                }
                send_position_alert("PROFIT_TARGET", symbol, details)
                print(f"50% profit alert sent for {symbol}")
            
            # Check for 100% profit target
            elif current_price <= position['take_profit_100'] and position['side'] == 'SHORT':
                profit_amount = (entry_price - current_price) * position['quantity']
                details = {
                    'percentage': 100,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'profit': profit_amount
                }
                send_position_alert("PROFIT_TARGET", symbol, details)
                print(f"100% profit alert sent for {symbol}")
            
            # Check for early warning at 80% of stop loss distance
            elif position['side'] == 'SHORT':
                warning_price = entry_price + (stop_loss - entry_price) * 0.8
                if current_price >= warning_price and current_price < stop_loss:
                    details = {
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'warning_level': '80%',
                        'side': position['side']
                    }
                    send_position_alert("STOP_WARNING", symbol, details)
                    print(f"Stop loss warning sent for {symbol}")
    
    def check_new_signals(self, market_data):
        """Check for new high-confidence signals"""
        from fast_signals import FastSignalGenerator
        
        try:
            signal_generator = FastSignalGenerator()
            signals = signal_generator.generate_fast_signals(market_data)
            
            # Filter for high confidence signals (90%+)
            high_confidence_signals = [
                signal for signal in signals 
                if signal.get('confidence', 0) >= 90 and signal.get('is_primary_trade', False)
            ]
            
            for signal in high_confidence_signals:
                symbol = signal['symbol']
                
                # Check if we already alerted for this signal recently
                alert_key = f"new_signal_{symbol}_{signal['action']}"
                if self._should_throttle_alert(alert_key, 7200):  # 2 hour throttle
                    continue
                
                # Send new signal alert
                details = {
                    'side': signal['action'],
                    'entry_price': signal['entry_price'],
                    'confidence': signal['confidence'],
                    'leverage': signal['leverage'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'expected_return': signal['expected_return'],
                    'strategy': signal.get('strategy_basis', 'Technical Analysis')
                }
                
                send_position_alert("NEW_SIGNAL", symbol, details)
                print(f"New signal alert sent for {symbol}")
                
                # Update throttle
                self.last_alerts[alert_key] = time.time()
                
        except Exception as e:
            print(f"Error checking new signals: {e}")
    
    def _should_throttle_alert(self, alert_key, throttle_seconds):
        """Check if alert should be throttled"""
        last_time = self.last_alerts.get(alert_key, 0)
        return (time.time() - last_time) < throttle_seconds

    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get current market data
                market_data = self.data_provider.get_market_data()
                if not market_data:
                    time.sleep(60)
                    continue
                
                # Get active positions
                positions = self.get_active_positions()
                
                # Check profit targets and stop losses
                self.check_profit_targets_and_stops(positions, market_data)
                
                # Check for new high-confidence signals
                self.check_new_signals(market_data)
                
                # Store current prices
                self.last_prices = {
                    symbol: data['price'] for symbol, data in market_data.items()
                }
                
                # Wait 2 minutes before next check
                time.sleep(120)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)
    
    def start_monitoring(self):
        """Start position monitoring in background"""
        if self.monitoring:
            return
            
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        print("Position monitoring started")
    
    def stop_monitoring(self):
        """Stop position monitoring"""
        self.monitoring = False
        print("Position monitoring stopped")

# Global monitor instance
position_monitor = PositionMonitor()

def start_position_monitoring():
    """Start monitoring ADA and SOL positions"""
    position_monitor.start_monitoring()