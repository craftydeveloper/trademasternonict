"""
Bybit Price Client - Direct Integration
Fetches real-time prices from Bybit futures API for authentic trading data
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BybitPriceClient:
    """Direct Bybit API integration for real-time futures prices"""
    
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradePro/1.0'
        })
    
    def get_futures_prices(self) -> Dict[str, float]:
        """Get real-time USDT futures prices from Bybit using public API"""
        try:
            # Try V5 API first
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'linear'}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('retCode') == 0 and 'result' in data:
                    prices = {}
                    
                    for ticker in data['result']['list']:
                        symbol = ticker.get('symbol', '')
                        last_price = ticker.get('lastPrice', '0')
                        
                        # Convert SOLUSDT -> SOL, LINKUSDT -> LINK, etc.
                        if symbol.endswith('USDT'):
                            base_symbol = symbol[:-4]  # Remove 'USDT'
                            try:
                                prices[base_symbol] = float(last_price)
                            except (ValueError, TypeError):
                                continue
                    
                    logger.info(f"Fetched {len(prices)} Bybit V5 futures prices")
                    return prices
            
            # Fallback to V2 public API
            logger.warning("V5 API failed, trying V2 public API")
            
            url = f"{self.base_url}/v2/public/tickers"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ret_code') == 0 and 'result' in data:
                    prices = {}
                    
                    for ticker in data['result']:
                        symbol = ticker.get('symbol', '')
                        last_price = ticker.get('last_price', '0')
                        
                        # Convert SOLUSDT -> SOL, LINKUSDT -> LINK, etc.
                        if symbol.endswith('USDT'):
                            base_symbol = symbol[:-4]  # Remove 'USDT'
                            try:
                                prices[base_symbol] = float(last_price)
                            except (ValueError, TypeError):
                                continue
                    
                    logger.info(f"Fetched {len(prices)} Bybit V2 futures prices")
                    return prices
            
            logger.error(f"Both Bybit APIs failed - V5: {response.status_code}")
            return {}
                
        except Exception as e:
            logger.error(f"Error fetching Bybit prices: {e}")
            return {}
    
    def get_specific_price(self, symbol: str) -> Optional[float]:
        """Get price for specific symbol from Bybit"""
        try:
            # Format symbol for Bybit (e.g., SOL -> SOLUSDT)
            bybit_symbol = f"{symbol}USDT"
            
            url = f"{self.base_url}/v5/market/tickers"
            params = {
                'category': 'linear',
                'symbol': bybit_symbol
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('retCode') == 0 and 'result' in data:
                    tickers = data['result']['list']
                    if tickers:
                        last_price = tickers[0].get('lastPrice', '0')
                        return float(last_price)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} price from Bybit: {e}")
            return None
    
    def get_market_summary(self) -> Dict:
        """Get Bybit market summary with key metrics"""
        try:
            prices = self.get_futures_prices()
            
            if not prices:
                return {}
            
            # Calculate basic market metrics
            total_symbols = len(prices)
            
            # Get key crypto prices
            key_cryptos = ['BTC', 'ETH', 'SOL', 'LINK', 'AVAX', 'ADA', 'DOT', 'UNI']
            key_prices = {symbol: prices.get(symbol, 0) for symbol in key_cryptos if symbol in prices}
            
            return {
                'timestamp': datetime.now().isoformat(),
                'source': 'Bybit Futures API',
                'total_symbols': total_symbols,
                'key_prices': key_prices,
                'all_prices': prices
            }
            
        except Exception as e:
            logger.error(f"Error getting Bybit market summary: {e}")
            return {}

def get_bybit_prices() -> Dict[str, float]:
    """Main function to get Bybit futures prices"""
    client = BybitPriceClient()
    return client.get_futures_prices()

def get_bybit_price(symbol: str) -> Optional[float]:
    """Get specific price from Bybit"""
    client = BybitPriceClient()
    return client.get_specific_price(symbol)

if __name__ == "__main__":
    print("=== BYBIT FUTURES PRICES ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    client = BybitPriceClient()
    
    # Test specific symbols
    test_symbols = ['SOL', 'LINK', 'AVAX', 'BTC', 'ETH', 'ADA']
    
    print("INDIVIDUAL PRICE CHECKS:")
    for symbol in test_symbols:
        price = client.get_specific_price(symbol)
        if price:
            print(f"• {symbol}: ${price:.2f}")
        else:
            print(f"• {symbol}: Price not found")
    
    print()
    
    # Get all prices
    all_prices = client.get_futures_prices()
    if all_prices:
        print(f"TOTAL SYMBOLS AVAILABLE: {len(all_prices)}")
        
        # Show top 10 by price
        top_prices = sorted(all_prices.items(), key=lambda x: x[1], reverse=True)[:10]
        print("\nTOP 10 BY PRICE:")
        for symbol, price in top_prices:
            print(f"• {symbol}: ${price:.2f}")
    
    print("\nNote: These are live Bybit futures prices")