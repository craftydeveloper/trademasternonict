"""
Bybit Price Override System
Forces all trading calculations to use exact Bybit market prices
"""

import logging
from typing import Dict, Optional
from exact_bybit_prices import get_exact_bybit_prices

logger = logging.getLogger(__name__)

class BybitPriceOverride:
    """Override system to force exact Bybit pricing across all calculations"""
    
    def __init__(self):
        self.exact_prices = {}
        self.last_update = None
        self._load_exact_prices()
    
    def _load_exact_prices(self):
        """Load exact Bybit prices"""
        try:
            self.exact_prices = get_exact_bybit_prices()
            logger.info(f"Loaded {len(self.exact_prices)} exact Bybit prices")
        except Exception as e:
            logger.error(f"Failed to load exact Bybit prices: {e}")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get exact Bybit price for symbol"""
        if not self.exact_prices:
            self._load_exact_prices()
        
        return self.exact_prices.get(symbol.upper())
    
    def get_all_prices(self) -> Dict[str, float]:
        """Get all exact Bybit prices"""
        if not self.exact_prices:
            self._load_exact_prices()
        
        return self.exact_prices.copy()
    
    def override_market_data(self, market_data: Dict) -> Dict:
        """Override market data with exact Bybit prices"""
        if not self.exact_prices:
            self._load_exact_prices()
        
        # Override with exact prices
        for symbol, exact_price in self.exact_prices.items():
            if symbol in market_data:
                # Preserve other data but override price
                market_data[symbol]['current_price'] = exact_price
                market_data[symbol]['price'] = exact_price
            else:
                # Add missing token with exact price
                market_data[symbol] = {
                    'current_price': exact_price,
                    'price': exact_price,
                    'price_change_percentage_24h': 2.5,
                    'market_cap': exact_price * 1000000,
                    'volume_24h': exact_price * 100000
                }
        
        logger.info(f"Applied Bybit price overrides for {len(self.exact_prices)} tokens")
        return market_data

# Global instance
bybit_override = BybitPriceOverride()

def get_bybit_price(symbol: str) -> Optional[float]:
    """Get exact Bybit price for symbol"""
    return bybit_override.get_price(symbol)

def override_with_bybit_prices(market_data: Dict) -> Dict:
    """Override market data with exact Bybit prices"""
    return bybit_override.override_market_data(market_data)