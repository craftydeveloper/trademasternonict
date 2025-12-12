"""
Comprehensive Market Data Feed - Multi-Source Aggregation
Provides enriched market data for ultra signal analysis
"""

import logging
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ComprehensiveMarketFeed:
    """Advanced market data aggregation from multiple sources"""
    
    def __init__(self):
        self.cache_duration = 60  # 1 minute cache
        self.last_update = None
        self.cached_data = {}
        
        # API endpoints (public, no auth required)
        self.sources = {
            'coinbase': 'https://api.coinbase.com/v2/exchange-rates',
            'binance': 'https://api.binance.com/api/v3/ticker/24hr',
            'coingecko': 'https://api.coingecko.com/api/v3/simple/price',
            'kraken': 'https://api.kraken.com/0/public/Ticker'
        }
        
        # Core trading pairs for comprehensive analysis
        self.symbols = [
            'BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC',
            'SHIB', 'LTC', 'LINK', 'UNI', 'ATOM', 'XLM', 'BCH', 'ETC', 'ICP', 'NEAR',
            'APT', 'ARB', 'OP', 'PEPE', 'AAVE', 'MKR', 'COMP', 'CRV', 'SUSHI'
        ]
    
    def get_comprehensive_market_data(self) -> Dict[str, Dict]:
        """Get comprehensive market data from multiple sources"""
        
        # Check cache validity
        if self._is_cache_valid():
            logger.info("Using cached comprehensive market data")
            return self.cached_data
        
        market_data = {}
        
        # Primary source: CoinGecko (most comprehensive)
        coingecko_data = self._fetch_coingecko_data()
        if coingecko_data:
            market_data.update(coingecko_data)
        
        # Secondary source: Binance (high-frequency updates)
        binance_data = self._fetch_binance_data()
        if binance_data:
            market_data = self._merge_data_sources(market_data, binance_data)
        
        # Tertiary source: Coinbase (institutional data)
        coinbase_data = self._fetch_coinbase_data()
        if coinbase_data:
            market_data = self._merge_data_sources(market_data, coinbase_data)
        
        # Enhance with calculated metrics
        market_data = self._enhance_market_data(market_data)
        
        # Update cache
        if market_data:
            self.cached_data = market_data
            self.last_update = datetime.utcnow()
            logger.info(f"Updated comprehensive market data with {len(market_data)} symbols")
        
        return market_data
    
    def _fetch_coingecko_data(self) -> Dict[str, Dict]:
        """Fetch data from CoinGecko API"""
        
        try:
            # Prepare symbol list for CoinGecko
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
                'XRP': 'ripple', 'SOL': 'solana', 'ADA': 'cardano',
                'DOGE': 'dogecoin', 'AVAX': 'avalanche-2', 'DOT': 'polkadot',
                'MATIC': 'matic-network', 'SHIB': 'shiba-inu', 'LTC': 'litecoin',
                'LINK': 'chainlink', 'UNI': 'uniswap', 'ATOM': 'cosmos',
                'XLM': 'stellar', 'BCH': 'bitcoin-cash', 'ETC': 'ethereum-classic',
                'ICP': 'internet-computer', 'NEAR': 'near', 'APT': 'aptos',
                'ARB': 'arbitrum', 'OP': 'optimism', 'PEPE': 'pepe',
                'AAVE': 'aave', 'MKR': 'maker', 'COMP': 'compound-governance-token'
            }
            
            coin_ids = ','.join(symbol_map.values())
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_ids,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {}
                for symbol, coin_id in symbol_map.items():
                    if coin_id in data:
                        coin_data = data[coin_id]
                        processed_data[symbol] = {
                            'price': coin_data.get('usd', 0),
                            'price_change_24h': coin_data.get('usd_24h_change', 0),
                            'volume_24h': coin_data.get('usd_24h_vol', 0),
                            'source': 'coingecko',
                            'timestamp': datetime.utcnow().isoformat(),
                            'high_24h': coin_data.get('usd', 0) * 1.02,  # Estimate
                            'low_24h': coin_data.get('usd', 0) * 0.98    # Estimate
                        }
                
                return processed_data
            
        except Exception as e:
            logger.error(f"CoinGecko API error: {e}")
        
        return {}
    
    def _fetch_binance_data(self) -> Dict[str, Dict]:
        """Fetch data from Binance API"""
        
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                processed_data = {}
                for ticker in data:
                    symbol = ticker['symbol']
                    
                    # Filter for USDT pairs and our target symbols
                    if symbol.endswith('USDT'):
                        base_symbol = symbol.replace('USDT', '')
                        
                        if base_symbol in self.symbols:
                            processed_data[base_symbol] = {
                                'price': float(ticker['lastPrice']),
                                'price_change_24h': float(ticker['priceChangePercent']),
                                'volume_24h': float(ticker['volume']) * float(ticker['lastPrice']),
                                'high_24h': float(ticker['highPrice']),
                                'low_24h': float(ticker['lowPrice']),
                                'source': 'binance',
                                'timestamp': datetime.utcnow().isoformat(),
                                'count': int(ticker['count'])  # Number of trades
                            }
                
                return processed_data
            
        except Exception as e:
            logger.error(f"Binance API error: {e}")
        
        return {}
    
    def _fetch_coinbase_data(self) -> Dict[str, Dict]:
        """Fetch data from Coinbase API"""
        
        try:
            # Get available trading pairs
            pairs_url = "https://api.coinbase.com/v2/exchange-rates"
            response = requests.get(pairs_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('data', {}).get('rates', {})
                
                processed_data = {}
                for symbol in self.symbols:
                    if symbol in rates:
                        price = float(rates[symbol])
                        if price > 0:
                            processed_data[symbol] = {
                                'price': 1.0 / price,  # Convert from USD to coin rate
                                'source': 'coinbase',
                                'timestamp': datetime.utcnow().isoformat(),
                                'institutional_grade': True
                            }
                
                return processed_data
            
        except Exception as e:
            logger.error(f"Coinbase API error: {e}")
        
        return {}
    
    def _merge_data_sources(self, primary_data: Dict, secondary_data: Dict) -> Dict:
        """Merge data from multiple sources intelligently"""
        
        merged_data = primary_data.copy()
        
        for symbol, data in secondary_data.items():
            if symbol in merged_data:
                # Merge additional fields from secondary source
                primary = merged_data[symbol]
                
                # Use more recent timestamp if available
                if 'timestamp' in data and 'timestamp' in primary:
                    if data['timestamp'] > primary['timestamp']:
                        primary['price'] = data['price']
                
                # Add unique fields
                for key, value in data.items():
                    if key not in primary:
                        primary[key] = value
                
                # Add source information
                sources = primary.get('sources', [primary.get('source', 'unknown')])
                if data.get('source') not in sources:
                    sources.append(data.get('source', 'unknown'))
                primary['sources'] = sources
                
            else:
                # Add new symbol from secondary source
                merged_data[symbol] = data
        
        return merged_data
    
    def _enhance_market_data(self, market_data: Dict) -> Dict:
        """Enhance market data with calculated metrics"""
        
        for symbol, data in market_data.items():
            try:
                price = data.get('price', 0)
                high_24h = data.get('high_24h', price)
                low_24h = data.get('low_24h', price)
                volume_24h = data.get('volume_24h', 0)
                price_change = data.get('price_change_24h', 0)
                
                # Calculate additional metrics
                if price > 0:
                    # Volatility measure
                    price_range = high_24h - low_24h
                    volatility = (price_range / price) * 100
                    data['volatility_24h'] = volatility
                    
                    # Range position
                    if price_range > 0:
                        data['range_position'] = (price - low_24h) / price_range
                    else:
                        data['range_position'] = 0.5
                    
                    # Momentum score
                    momentum_score = abs(price_change) + (volatility * 0.1)
                    data['momentum_score'] = momentum_score
                    
                    # Volume score (normalized)
                    volume_score = min(volume_24h / 1000000, 10.0)
                    data['volume_score'] = volume_score
                    
                    # Overall trading score
                    trading_score = (
                        momentum_score * 0.4 +
                        volume_score * 0.3 +
                        volatility * 0.2 +
                        abs(data['range_position'] - 0.5) * 20 * 0.1
                    )
                    data['trading_score'] = trading_score
                    
                    # Market cap tier estimation
                    if volume_24h > 1000000000:  # $1B+ volume
                        data['market_tier'] = 'large_cap'
                    elif volume_24h > 100000000:  # $100M+ volume
                        data['market_tier'] = 'mid_cap'
                    else:
                        data['market_tier'] = 'small_cap'
                
            except Exception as e:
                logger.warning(f"Error enhancing data for {symbol}: {e}")
        
        return market_data
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        
        if not self.last_update or not self.cached_data:
            return False
        
        time_diff = datetime.utcnow() - self.last_update
        return time_diff.total_seconds() < self.cache_duration
    
    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get top trading opportunities ranked by composite score"""
        
        market_data = self.get_comprehensive_market_data()
        
        # Convert to list and sort by trading score
        opportunities = []
        for symbol, data in market_data.items():
            data['symbol'] = symbol
            opportunities.append(data)
        
        # Sort by trading score
        opportunities.sort(key=lambda x: x.get('trading_score', 0), reverse=True)
        
        return opportunities[:limit]
    
    def get_market_overview(self) -> Dict:
        """Get comprehensive market overview"""
        
        market_data = self.get_comprehensive_market_data()
        
        if not market_data:
            return {}
        
        # Calculate market metrics
        total_symbols = len(market_data)
        positive_moves = sum(1 for data in market_data.values() 
                           if data.get('price_change_24h', 0) > 0)
        
        avg_change = sum(data.get('price_change_24h', 0) 
                        for data in market_data.values()) / total_symbols
        
        avg_volatility = sum(data.get('volatility_24h', 0) 
                           for data in market_data.values()) / total_symbols
        
        total_volume = sum(data.get('volume_24h', 0) 
                          for data in market_data.values())
        
        # Market sentiment
        market_sentiment = positive_moves / total_symbols
        
        # Volatility regime
        if avg_volatility > 8:
            volatility_regime = 'high'
        elif avg_volatility > 4:
            volatility_regime = 'elevated'
        else:
            volatility_regime = 'normal'
        
        return {
            'total_symbols': total_symbols,
            'market_sentiment': market_sentiment,
            'avg_price_change': avg_change,
            'avg_volatility': avg_volatility,
            'total_volume_24h': total_volume,
            'volatility_regime': volatility_regime,
            'positive_symbols': positive_moves,
            'negative_symbols': total_symbols - positive_moves,
            'last_updated': datetime.utcnow().isoformat(),
            'data_quality': len([d for d in market_data.values() 
                               if len(d.get('sources', [])) > 1])
        }

def get_comprehensive_market_feed() -> Dict[str, Dict]:
    """Main function to get comprehensive market data"""
    
    feed = ComprehensiveMarketFeed()
    return feed.get_comprehensive_market_data()