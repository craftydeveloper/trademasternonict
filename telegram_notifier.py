"""
Telegram Notifier - Send alerts for new trading signals
"""
import os
import logging
import requests
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send trading signal alerts to Telegram"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.last_signals = {}
        
        if self.bot_token and self.chat_id:
            logger.info("Telegram notifications enabled")
        else:
            logger.info("Telegram notifications disabled - missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    
    def is_enabled(self) -> bool:
        """Check if Telegram is configured"""
        return bool(self.bot_token and self.chat_id)
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to Telegram channel"""
        if not self.is_enabled():
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """Send a new trading signal alert"""
        if not self.is_enabled():
            return False
        
        symbol = signal.get('symbol', 'UNKNOWN')
        action = signal.get('action', 'HOLD')
        
        if action == 'HOLD':
            return True
        
        last_action = self.last_signals.get(symbol)
        if last_action == action:
            return True
        
        self.last_signals[symbol] = action
        
        confidence = signal.get('confidence', 0)
        current_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', 0)
        prediction = signal.get('prediction', '')
        signal_type = signal.get('signal_type', '')
        htf_trend = signal.get('htf_trend', 'N/A')
        
        if current_price < 1:
            price_fmt = f"${current_price:.6f}"
            sl_fmt = f"${stop_loss:.6f}"
            tp_fmt = f"${take_profit:.6f}"
        else:
            price_fmt = f"${current_price:.4f}"
            sl_fmt = f"${stop_loss:.4f}"
            tp_fmt = f"${take_profit:.4f}"
        
        emoji = "🟢" if action == "BUY" else "🔴"
        direction = "LONG" if action == "BUY" else "SHORT"
        
        message = f"""
{emoji} <b>NEW SIGNAL: {symbol}</b>

<b>Direction:</b> {direction}
<b>Entry:</b> {price_fmt}
<b>Stop Loss:</b> {sl_fmt}
<b>Take Profit:</b> {tp_fmt}
<b>Confidence:</b> {confidence:.0f}%
<b>HTF Trend:</b> {htf_trend}

<i>{prediction}</i>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())
    
    def send_bias_change_alert(self, symbol: str, previous: str, new: str, price: float) -> bool:
        """Send alert when signal bias changes"""
        if not self.is_enabled():
            return False
        
        if price < 1:
            price_fmt = f"${price:.6f}"
        else:
            price_fmt = f"${price:.4f}"
        
        emoji = "⚠️"
        message = f"""
{emoji} <b>BIAS CHANGE: {symbol}</b>

<b>Previous:</b> {previous}
<b>New:</b> {new}
<b>Price:</b> {price_fmt}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message.strip())


notifier = TelegramNotifier()

def send_telegram_alert(message: str) -> bool:
    """Convenience function to send a message"""
    return notifier.send_message(message)

def send_signal_to_telegram(signal: Dict) -> bool:
    """Send signal alert to Telegram"""
    return notifier.send_signal_alert(signal)

def send_bias_change_to_telegram(symbol: str, previous: str, new: str, price: float) -> bool:
    """Send bias change alert to Telegram"""
    return notifier.send_bias_change_alert(symbol, previous, new, price)

def reload_credentials():
    """Reload Telegram credentials from environment"""
    global notifier
    notifier = TelegramNotifier()
    return notifier.is_enabled()
