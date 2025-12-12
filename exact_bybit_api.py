"""
Exact Bybit API Price Fetcher
Gets real-time exact prices directly from Bybit public API
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ExactBybitAPI:
    """Fetch exact prices from Bybit public API"""
    
    def __init__(self):
        self.base_url = "https://api.bybit.com"
    
    def get_exact_price(self, symbol: str) -> Optional[float]:
        """Get exact price for a specific symbol from Bybit"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                "category": "linear",
                "symbol": f"{symbol}USDT"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("retCode") == 0:
                    result = data.get("result", {}).get("list", [])
                    if result:
                        price = float(result[0].get("lastPrice", 0))
                        logger.info(f"Exact Bybit {symbol}: ${price}")
                        return price
            
            logger.warning(f"Failed to get exact price for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching exact {symbol} price: {e}")
            return None
    
    def get_multiple_prices(self, symbols: list) -> Dict[str, float]:
        """Get exact prices for multiple symbols"""
        prices = {}
        
        try:
            # Get all linear futures tickers at once
            url = f"{self.base_url}/v5/market/tickers"
            params = {"category": "linear"}
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("retCode") == 0:
                    all_tickers = data.get("result", {}).get("list", [])
                    
                    # Extract prices for requested symbols
                    for ticker in all_tickers:
                        symbol = ticker.get("symbol", "")
                        if symbol.endswith("USDT"):
                            token = symbol.replace("USDT", "")
                            if token in symbols:
                                price = float(ticker.get("lastPrice", 0))
                                if price > 0:
                                    prices[token] = price
                                    logger.info(f"Exact Bybit {token}: ${price}")
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching multiple Bybit prices: {e}")
            return {}

def get_exact_bybit_price(symbol: str) -> Optional[float]:
    """Get exact price for a symbol from Bybit"""
    api = ExactBybitAPI()
    return api.get_exact_price(symbol)

def get_exact_bybit_prices(symbols: list) -> Dict[str, float]:
    """Get exact prices for multiple symbols from Bybit"""
    api = ExactBybitAPI()
    return api.get_multiple_prices(symbols)