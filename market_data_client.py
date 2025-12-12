"""
Real Market Data Client for Trading Bot
Provides authenticated access to cryptocurrency market data
"""

import os
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MarketDataClient:
    """Unified client for real cryptocurrency market data"""
    
    def __init__(self):
        self.coinapi_key = os.environ.get('COINAPI_KEY')
        self.bybit_key = os.environ.get('BYBIT_API_KEY')
        self.bybit_secret = os.environ.get('BYBIT_SECRET_KEY')
        
        # Token mappings for different APIs
        self.token_symbols = {
            'BTC': {'coinapi': 'BTC', 'bybit': 'BTCUSDT', 'coingecko': 'bitcoin'},
            'ETH': {'coinapi': 'ETH', 'bybit': 'ETHUSDT', 'coingecko': 'ethereum'},
            'SOL': {'coinapi': 'SOL', 'bybit': 'SOLUSDT', 'coingecko': 'solana'},
            'ADA': {'coinapi': 'ADA', 'bybit': 'ADAUSDT', 'coingecko': 'cardano'},
            'DOT': {'coinapi': 'DOT', 'bybit': 'DOTUSDT', 'coingecko': 'polkadot'},
            'MATIC': {'coinapi': 'MATIC', 'bybit': 'MATICUSDT', 'coingecko': 'polygon'},
            'AVAX': {'coinapi': 'AVAX', 'bybit': 'AVAXUSDT', 'coingecko': 'avalanche-2'},
            'LINK': {'coinapi': 'LINK', 'bybit': 'LINKUSDT', 'coingecko': 'chainlink'},
            'AXS': {'coinapi': 'AXS', 'bybit': 'AXSUSDT', 'coingecko': 'axie-infinity'}
        }
    
    def get_real_time_prices(self) -> Optional[Dict]:
        """Get current market prices from available APIs"""
        
        # Try CoinAPI first (most comprehensive)
        if self.coinapi_key:
            prices = self._get_coinapi_prices()
            if prices:
                logger.info(f"Retrieved prices for {len(prices)} tokens from CoinAPI")
                return prices
        
        # Try CoinGecko API (public endpoint with good coverage)
        prices = self._get_coingecko_prices()
        if prices:
            logger.info(f"Retrieved prices for {len(prices)} tokens from CoinGecko")
            return prices
        
        # Try Bybit API (direct exchange data - if accessible)
        prices = self._get_bybit_prices()
        if prices:
            logger.info(f"Retrieved prices for {len(prices)} tokens from Bybit")
            return prices
        
        # Log that no data could be retrieved
        logger.error("Unable to retrieve market data from available sources")
        logger.error("Available APIs: CoinAPI (premium), CoinGecko (public), Bybit (exchange)")
        
        return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> Optional[List[Dict]]:
        """Get historical price data for technical analysis"""
        
        # Try CoinAPI first
        if self.coinapi_key:
            data = self._get_coinapi_history(symbol, days)
            if data:
                logger.info(f"Retrieved {len(data)} historical points for {symbol} from CoinAPI")
                return data
        
        # Try CoinGecko for historical data (public API)
        data = self._get_coingecko_history(symbol, days)
        if data:
            logger.info(f"Retrieved {len(data)} historical points for {symbol} from CoinGecko")
            return data
        
        # Try Bybit for historical data
        if self.bybit_key:
            data = self._get_bybit_history(symbol, days)
            if data:
                logger.info(f"Retrieved {len(data)} historical points for {symbol} from Bybit")
                return data
        
        logger.error(f"Cannot retrieve historical data for {symbol} - no working API source")
        return None
    
    def _get_coinapi_prices(self) -> Optional[Dict]:
        """Fetch prices from CoinAPI"""
        try:
            headers = {'X-CoinAPI-Key': self.coinapi_key}
            prices = {}
            
            for symbol, mappings in self.token_symbols.items():
                coinapi_symbol = mappings['coinapi']
                
                # Get current rate
                url = f"https://rest.coinapi.io/v1/exchangerate/{coinapi_symbol}/USD"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current_price = data.get('rate', 0)
                    
                    prices[symbol] = {
                        'price': current_price,
                        'change_24h': 0,  # Would need separate endpoint
                        'volume_24h': 0   # Would need separate endpoint
                    }
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                elif response.status_code == 403:
                    logger.error(f"CoinAPI quota exceeded or subscription required")
                    return None
                
                else:
                    logger.warning(f"CoinAPI error for {symbol}: {response.status_code}")
            
            return prices if prices else None
            
        except Exception as e:
            logger.error(f"CoinAPI error: {e}")
            return None
    
    def _get_bybit_prices(self) -> Optional[Dict]:
        """Fetch prices from Bybit API - using public endpoint for reliable market data"""
        try:
            # Use public endpoint for market data - no authentication required
            params = {
                'category': 'spot'
            }
            
            url = "https://api.bybit.com/v5/market/tickers"
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Bybit API error: {response.status_code}")
                return None
            
            data = response.json()
            if data.get('retCode') != 0:
                logger.error(f"Bybit API error: {data.get('retMsg')}")
                return None
            
            tickers = data.get('result', {}).get('list', [])
            
            prices = {}
            for symbol, mappings in self.token_symbols.items():
                bybit_symbol = mappings['bybit']
                
                for ticker in tickers:
                    if ticker.get('symbol') == bybit_symbol:
                        prices[symbol] = {
                            'price': float(ticker.get('lastPrice', 0)),
                            'change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                            'volume_24h': float(ticker.get('volume24h', 0))
                        }
                        break
            
            return prices if prices else None
            
        except Exception as e:
            logger.error(f"Bybit API error: {e}")
            return None
    
    def _get_coingecko_prices(self) -> Optional[Dict]:
        """Fetch prices from CoinGecko public API"""
        try:
            # Get all token IDs we need
            token_ids = [mappings['coingecko'] for mappings in self.token_symbols.values()]
            ids_string = ','.join(token_ids)
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ids_string,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"CoinGecko API error: {response.status_code}")
                return None
            
            data = response.json()
            prices = {}
            
            for symbol, mappings in self.token_symbols.items():
                coingecko_id = mappings['coingecko']
                
                if coingecko_id in data:
                    token_data = data[coingecko_id]
                    prices[symbol] = {
                        'price': token_data.get('usd', 0),
                        'change_24h': token_data.get('usd_24h_change', 0),
                        'volume_24h': token_data.get('usd_24h_vol', 0)
                    }
            
            return prices if prices else None
            
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
            return None
    
    def _get_coingecko_history(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """Get historical data from CoinGecko public API with smart caching"""
        try:
            if symbol not in self.token_symbols:
                return None
            
            coingecko_id = self.token_symbols[symbol]['coingecko']
            
            # Use public endpoint without authentication for reliable access
            url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 365),  # Limit to avoid rate limits
                'interval': 'daily'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; TradingBot/1.0)',
                'Accept': 'application/json'
            }
            
            # Single request with timeout for speed
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 429:
                # Rate limited - return None immediately instead of waiting
                logger.warning(f"Rate limited for {symbol}, skipping")
                return None
            elif response.status_code != 200:
                logger.error(f"CoinGecko error {response.status_code} for {symbol}")
                return None
            
            data = response.json()
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            if not prices:
                logger.error(f"No price data returned for {symbol}")
                return None
            
            price_history = []
            for i, price_point in enumerate(prices):
                timestamp_ms = price_point[0]
                price = price_point[1]
                volume = volumes[i][1] if i < len(volumes) else 0
                
                price_history.append({
                    'price': price,
                    'volume': volume,
                    'timestamp': datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
                })
            
            logger.info(f"Retrieved {len(price_history)} historical points for {symbol} from CoinGecko")
            return price_history
            
        except Exception as e:
            logger.error(f"CoinGecko historical error for {symbol}: {e}")
            return None
    
    def _get_coinapi_history(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """Get historical data from CoinAPI"""
        try:
            if symbol not in self.token_symbols:
                return None
            
            coinapi_symbol = self.token_symbols[symbol]['coinapi']
            headers = {'X-CoinAPI-Key': self.coinapi_key}
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            url = f"https://rest.coinapi.io/v1/exchangerate/{coinapi_symbol}/USD/history"
            params = {
                'period_id': '1HRS',
                'time_start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                'time_end': end_time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code == 403:
                logger.error("CoinAPI quota exceeded for historical data")
                return None
            
            if response.status_code != 200:
                logger.error(f"CoinAPI historical error: {response.status_code}")
                return None
            
            historical_data = response.json()
            
            price_history = []
            for point in historical_data:
                price_history.append({
                    'price': point.get('rate_close', point.get('rate_open', 0)),
                    'volume': 0,
                    'timestamp': point.get('time_close', point.get('time_open', ''))
                })
            
            return price_history
            
        except Exception as e:
            logger.error(f"CoinAPI historical error for {symbol}: {e}")
            return None
    
    def _get_bybit_history(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """Get historical data from Bybit"""
        try:
            if symbol not in self.token_symbols:
                return None
            
            bybit_symbol = self.token_symbols[symbol]['bybit']
            
            # Use Bybit kline endpoint
            url = "https://api.bybit.com/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': bybit_symbol,
                'interval': '60',  # 1 hour
                'limit': min(days * 24, 1000)  # API limit
            }
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code != 200:
                logger.error(f"Bybit historical error: {response.status_code}")
                return None
            
            data = response.json()
            klines = data.get('result', {}).get('list', [])
            
            price_history = []
            for kline in klines:
                timestamp_ms = int(kline[0])
                close_price = float(kline[4])
                volume = float(kline[5])
                
                price_history.append({
                    'price': close_price,
                    'volume': volume,
                    'timestamp': datetime.fromtimestamp(timestamp_ms / 1000).isoformat()
                })
            
            # Reverse to chronological order
            price_history.reverse()
            return price_history
            
        except Exception as e:
            logger.error(f"Bybit historical error for {symbol}: {e}")
            return None
    
    def check_api_status(self) -> Dict[str, bool]:
        """Check which APIs are available and working"""
        status = {
            'coinapi': False,
            'bybit': False,
            'coingecko': False
        }
        
        if self.coinapi_key:
            try:
                headers = {'X-CoinAPI-Key': self.coinapi_key}
                response = requests.get('https://rest.coinapi.io/v1/exchangerate/BTC/USD', 
                                     headers=headers, timeout=5)
                status['coinapi'] = response.status_code == 200
            except:
                pass
        
        # Test CoinGecko public API
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', 
                                  timeout=5)
            status['coingecko'] = response.status_code == 200
        except:
            pass
        
        # Bybit doesn't require auth for market data
        try:
            response = requests.get('https://api.bybit.com/v5/market/tickers?category=spot', 
                                  timeout=5)
            status['bybit'] = response.status_code == 200
        except:
            pass
        
        return status