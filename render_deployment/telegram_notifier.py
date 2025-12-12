"""
Enhanced Telegram Notifier for Balanced Trading
Auto-monitoring with bug fixing and comprehensive alerts
"""
import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Simple Telegram notifications for trading alerts"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.last_alerts = {}
        
    def send_message(self, message: str, urgent: bool = False) -> bool:
        """Send message via Telegram API"""
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram credentials not configured")
            return False
            
        try:
            # Add urgency and timestamp
            timestamp = datetime.now().strftime('%H:%M:%S')
            if urgent:
                message = f"🚨 URGENT ALERT 🚨\n⏰ {timestamp}\n\n" + message
            else:
                message = f"📊 System Update\n⏰ {timestamp}\n\n" + message
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                logger.info("Telegram alert sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_position_alert(self, action: str, symbol: str, details: Dict) -> bool:
        """Send position management alert"""
        if action == "PROFIT_TARGET":
            message = f"""
<b>💰 PROFIT TARGET REACHED</b>

<b>Symbol:</b> {symbol}
<b>Action:</b> Take {details['percentage']}% Profit
<b>Current Price:</b> ${details['current_price']:.4f}
<b>Entry Price:</b> ${details['entry_price']:.4f}
<b>Profit:</b> ${details['profit']:.2f}

<b>⚡ Action Required:</b> Close {details['percentage']}% of position now
"""
        
        elif action == "STOP_LOSS":
            message = f"""
<b>🚨 STOP LOSS TRIGGERED</b>

<b>Symbol:</b> {symbol}
<b>Action:</b> Cut Loss Immediately
<b>Current Price:</b> ${details['current_price']:.4f}
<b>Entry Price:</b> ${details['entry_price']:.4f}
<b>Stop Loss:</b> ${details['stop_loss']:.4f}
<b>Loss Amount:</b> ${details['loss_amount']:.2f}
<b>P&L:</b> {details['pnl_percent']:.1f}%

<b>⚡ URGENT ACTION:</b> Close {symbol} {details['side']} position NOW
Risk management requires immediate exit
"""
        
        elif action == "STOP_WARNING":
            message = f"""
<b>⚠️ STOP LOSS WARNING</b>

<b>Symbol:</b> {symbol}
<b>Warning:</b> Approaching stop loss level
<b>Current Price:</b> ${details['current_price']:.4f}
<b>Entry Price:</b> ${details['entry_price']:.4f}
<b>Stop Loss:</b> ${details['stop_loss']:.4f}

<b>📊 Status:</b> Position moving against you
Consider reducing position size or preparing to exit

<b>Action:</b> Monitor closely for potential stop loss
"""
        
        elif action == "NEW_SIGNAL":
            message = f"""
<b>🎯 NEW ULTRA-HIGH CONFIDENCE SIGNAL</b>

<b>Symbol:</b> {symbol}
<b>Action:</b> {details['side']} (New Position)
<b>Entry Price:</b> ${details['entry_price']:.4f}
<b>Confidence:</b> {details['confidence']:.1f}%
<b>Leverage:</b> {details['leverage']}x

<b>Risk/Reward:</b>
Stop Loss: ${details['stop_loss']:.4f}
Take Profit: ${details['take_profit']:.4f}
Expected Return: ${details['expected_return']:.2f}

<b>Strategy:</b> {details.get('strategy', 'Advanced Technical Analysis')}

<b>⚡ ACTION:</b> Consider {symbol} {details['side']} position
This {details['confidence']:.1f}% signal offers good trading opportunity
"""
        
        elif action == "PORTFOLIO_UPDATE":
            message = f"""
<b>📊 PORTFOLIO UPDATE</b>

<b>Current Balance:</b> ${details['balance']:.2f}
<b>Total P&L:</b> ${details['pnl']:.2f} ({details['pnl_percent']:.1f}%)
<b>Active Positions:</b> {details['active_positions']}

<b>$50K Progress:</b>
Target: ${details['target_amount']:,}
Progress: {details['progress_percent']:.2f}%
Days Remaining: {details['days_remaining']}
Daily Rate Needed: {details['daily_rate_needed']:.2f}%

<b>Status:</b> {details['performance_status']}
"""
        else:
            return False
        
        return self.send_message(message, urgent=(action in ["NEW_SIGNAL", "PROFIT_TARGET", "STOP_LOSS"]))
    
    def check_and_alert_positions(self, positions: List[Dict], market_prices: Dict):
        """Check positions and send alerts if needed"""
        for position in positions:
            symbol = position['symbol']
            if symbol not in market_prices:
                continue
                
            current_price = market_prices[symbol]['price']
            entry_price = position['avg_entry']
            side = position['side']
            
            # Calculate P&L
            if side == 'LONG':
                pnl_percent = ((current_price / entry_price) - 1) * 100
            else:  # SHORT
                pnl_percent = ((entry_price / current_price) - 1) * 100
            
            # Check for stop loss (most critical)
            if pnl_percent <= -8:  # 8% loss threshold
                alert_key = f"stop_loss_{symbol}"
                if not self._should_throttle_alert(alert_key, 300):  # 5 minute throttle
                    details = {
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'loss_amount': abs(position['net_quantity'] * (current_price - entry_price)),
                        'pnl_percent': pnl_percent,
                        'side': side
                    }
                    self.send_position_alert("STOP_LOSS", symbol, details)
                    self.last_alerts[alert_key] = datetime.now().timestamp()
            
            # Check for 50% profit target
            elif pnl_percent >= 50:
                alert_key = f"profit_50_{symbol}"
                if not self._should_throttle_alert(alert_key, 3600):  # 1 hour throttle
                    details = {
                        'percentage': 50,
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'profit': position['net_quantity'] * abs(current_price - entry_price) / 2
                    }
                    self.send_position_alert("PROFIT_TARGET", symbol, details)
                    self.last_alerts[alert_key] = datetime.now().timestamp()
    
    def _should_throttle_alert(self, alert_key: str, throttle_seconds: int) -> bool:
        """Check if alert should be throttled"""
        last_time = self.last_alerts.get(alert_key, 0)
        return (datetime.now().timestamp() - last_time) < throttle_seconds

# Global notifier instance
telegram_notifier = TelegramNotifier()

def send_alert(message: str, urgent: bool = False) -> bool:
    """Send Telegram alert"""
    return telegram_notifier.send_message(message, urgent)

def send_position_alert(action: str, symbol: str, details: Dict) -> bool:
    """Send position alert"""
    return telegram_notifier.send_position_alert(action, symbol, details)