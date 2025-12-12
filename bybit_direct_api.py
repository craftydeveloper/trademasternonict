"""
Direct Bybit API Integration - Real-time Price Synchronization
Fetches exact prices directly from Bybit's public API for all futures pairs
"""
import requests
import logging
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)

class BybitDirectAPI:
    """Direct integration with Bybit public API for exact price matching"""
    
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.cache = {}
        self.cache_expiry = 0
        self.cache_duration = 30  # 30 seconds cache
        
    def get_all_futures_prices(self) -> Dict[str, float]:
        """Get all USDT futures prices directly from Bybit"""
        try:
            # Check cache first
            if time.time() < self.cache_expiry and self.cache:
                logger.info(f"Using cached Bybit prices: {len(self.cache)} pairs")
                return self.cache
            
            # Fetch fresh data from Bybit
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                "category": "linear",  # USDT futures
                "limit": "200"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('retCode') != 0:
                raise Exception(f"Bybit API error: {data.get('retMsg')}")
            
            prices = {}
            for ticker in data.get('result', {}).get('list', []):
                symbol = ticker.get('symbol', '')
                price = ticker.get('lastPrice')
                
                # Extract base symbol (remove USDT suffix)
                if symbol.endswith('USDT') and price:
                    base_symbol = symbol[:-4]  # Remove 'USDT'
                    prices[base_symbol] = float(price)
            
            # Update cache
            self.cache = prices
            self.cache_expiry = time.time() + self.cache_duration
            
            logger.info(f"Fetched {len(prices)} live Bybit futures prices")
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching Bybit prices: {e}")
            # Return cached data if available
            if self.cache:
                logger.info(f"Returning cached Bybit prices due to error: {len(self.cache)} pairs")
                return self.cache
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get specific price for a symbol"""
        prices = self.get_all_futures_prices()
        return prices.get(symbol.upper())
    
    def sync_market_data(self, market_data: Dict) -> Dict:
        """Synchronize market data with exact Bybit prices"""
        bybit_prices = self.get_all_futures_prices()
        
        if not bybit_prices:
            logger.warning("No Bybit prices available, returning original data")
            return market_data
        
        synced_data = {}
        sync_count = 0
        
        for symbol, data in market_data.items():
            if isinstance(data, dict):
                synced_data[symbol] = data.copy()
                
                # Update with exact Bybit price
                if symbol.upper() in bybit_prices:
                    exact_price = bybit_prices[symbol.upper()]
                    synced_data[symbol]['price'] = exact_price
                    synced_data[symbol]['price_usd'] = exact_price
                    sync_count += 1
                    
        logger.info(f"Synchronized {sync_count} prices with Bybit")
        return synced_data

# Global instance
bybit_api = BybitDirectAPI()

def get_bybit_live_prices() -> Dict[str, float]:
    """Get live Bybit futures prices"""
    return bybit_api.get_all_futures_prices()

def get_bybit_price(symbol: str) -> Optional[float]:
    """Get specific price from Bybit"""
    return bybit_api.get_price(symbol)

def sync_with_bybit(market_data: Dict) -> Dict:
    """Sync market data with exact Bybit prices"""
    return bybit_api.sync_market_data(market_data)