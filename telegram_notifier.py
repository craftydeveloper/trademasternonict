"""
Telegram Notifier - DISABLED
All Telegram functionality has been disabled per user request
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram notifications completely disabled"""
    
    def __init__(self):
        # All Telegram functionality disabled
        self.bot_token = None
        self.chat_id = None
        self.last_alerts = {}
        logger.info("Telegram notifications permanently disabled")
        
    def send_message(self, message: str, urgent: bool = False) -> bool:
        """Telegram disabled - no messages sent"""
        return True
    
    def send_position_alert(self, action: str, symbol: str, details: Dict) -> bool:
        """Telegram disabled - no alerts sent"""
        return True
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """Telegram disabled - no signal alerts"""
        return True
    
    def send_daily_update(self, status: Dict) -> bool:
        """Telegram disabled - no daily updates"""
        return True
    
    def send_system_status(self, status: str, details: str = "") -> bool:
        """Telegram disabled - no system status"""
        return True

# Convenience function for backward compatibility
def send_telegram_alert(message: str, urgent: bool = False) -> bool:
    """All Telegram functionality disabled"""
    return True

# Global instance (disabled)
notifier = TelegramNotifier()