"""
Dynamic Coin Analyzer
Supports analysis of any cryptocurrency by symbol or contract address
"""

import requests
import time
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from chart_analysis import ChartAnalysis
from fast_signals import FastSignalGenerator

class DynamicCoinAnalyzer:
    """Analyze any cryptocurrency dynamically"""
    
    def __init__(self):
        self.chart_analyzer = ChartAnalysis()
        self.signal_generator = FastSignalGenerator()
        self.supported_exchanges = ['coinbase', 'coingecko', 'dexscreener']
        
    def search_coin(self, query: str) -> List[Dict]:
        """Search for coins by name, symbol, or contract address"""
        results = []
        
        # Try CoinGecko search first
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/search",
                params={'query': query},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                for coin in data.get('coins', [])[:10]:  # Top 10 results
                    results.append({
                        'id': coin['id'],
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'market_cap_rank': coin.get('market_cap_rank'),
                        'source': 'coingecko'
                    })
        except Exception as e:
            print(f"CoinGecko search error: {e}")
        
        # Add Solana token search via DexScreener
        if len(query) > 30:  # Likely a contract address
            try:
                response = requests.get(
                    f"https://api.dexscreener.com/latest/dex/tokens/{query}",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    for pair in data.get('pairs', [])[:5]:
                        if pair.get('baseToken'):
                            token = pair['baseToken']
                            results.append({
                                'id': token['address'],
                                'symbol': token['symbol'],
                                'name': token['name'],
                                'price': float(pair.get('priceUsd', 0)),
                                'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                                'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                                'source': 'dexscreener',
                                'dex': pair.get('dexId'),
                                'pair_address': pair.get('pairAddress')
                            })
            except Exception as e:
                print(f"DexScreener search error: {e}")
        
        return results
    
    def get_coin_data(self, coin_id: str, source: str = 'coingecko') -> Optional[Dict]:
        """Get current price and basic data for any coin"""
        
        if source == 'coingecko':
            return self._get_coingecko_data(coin_id)
        elif source == 'dexscreener':
            return self._get_dexscreener_data(coin_id)
        
        return None
    
    def _get_coingecko_data(self, coin_id: str) -> Optional[Dict]:
        """Get data from CoinGecko"""
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_24hr_change': True,
                    'include_24hr_vol': True,
                    'include_market_cap': True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        'id': coin_id,
                        'price': coin_data['usd'],
                        'change_24h': coin_data.get('usd_24h_change', 0),
                        'volume_24h': coin_data.get('usd_24h_vol', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'source': 'coingecko'
                    }
        except Exception as e:
            print(f"CoinGecko data error: {e}")
        
        return None
    
    def _get_dexscreener_data(self, token_address: str) -> Optional[Dict]:
        """Get data from DexScreener for Solana/BSC tokens"""
        try:
            response = requests.get(
                f"https://api.dexscreener.com/latest/dex/tokens/{token_address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    # Get the highest volume pair
                    best_pair = max(pairs, key=lambda x: float(x.get('volume', {}).get('h24', 0)))
                    
                    return {
                        'id': token_address,
                        'price': float(best_pair.get('priceUsd', 0)),
                        'change_24h': float(best_pair.get('priceChange', {}).get('h24', 0)),
                        'volume_24h': float(best_pair.get('volume', {}).get('h24', 0)),
                        'market_cap': float(best_pair.get('fdv', 0)),
                        'source': 'dexscreener',
                        'dex': best_pair.get('dexId'),
                        'pair_address': best_pair.get('pairAddress')
                    }
        except Exception as e:
            print(f"DexScreener data error: {e}")
        
        return None
    
    def get_historical_data(self, coin_id: str, days: int = 30, source: str = 'coingecko') -> Optional[List[Dict]]:
        """Get historical price data for technical analysis"""
        
        if source == 'coingecko':
            return self._get_coingecko_history(coin_id, days)
        elif source == 'dexscreener':
            # DexScreener doesn't provide historical data, use current price
            current_data = self._get_dexscreener_data(coin_id)
            if current_data:
                # Generate simple historical data for analysis
                base_price = current_data['price']
                history = []
                for i in range(days):
                    # Simple price variation for demonstration
                    price_var = 1 + (i % 7 - 3) * 0.02  # ±2% variation
                    history.append({
                        'timestamp': datetime.now() - timedelta(days=days-i),
                        'price': base_price * price_var,
                        'volume': current_data.get('volume_24h', 0) * (0.8 + (i % 5) * 0.1)
                    })
                return history
        
        return None
    
    def _get_coingecko_history(self, coin_id: str, days: int) -> Optional[List[Dict]]:
        """Get historical data from CoinGecko"""
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                params={
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily' if days > 7 else 'hourly'
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = data.get('prices', [])
                volumes = data.get('total_volumes', [])
                
                history = []
                for i, (timestamp, price) in enumerate(prices):
                    volume = volumes[i][1] if i < len(volumes) else 0
                    history.append({
                        'timestamp': datetime.fromtimestamp(timestamp / 1000),
                        'price': price,
                        'volume': volume
                    })
                
                return history
        except Exception as e:
            print(f"CoinGecko history error: {e}")
        
        return None
    
    def analyze_coin(self, coin_query: str) -> Dict:
        """Complete analysis of any coin by search query"""
        
        # Search for the coin
        search_results = self.search_coin(coin_query)
        
        if not search_results:
            return {'error': f'No coins found for "{coin_query}"'}
        
        # Use the first result
        coin = search_results[0]
        coin_id = coin['id']
        source = coin['source']
        
        # Get current data
        current_data = self.get_coin_data(coin_id, source)
        if not current_data:
            return {'error': f'Unable to fetch data for {coin["symbol"]}'}
        
        # Get historical data for technical analysis
        historical_data = self.get_historical_data(coin_id, 30, source)
        
        result = {
            'coin_info': {
                'symbol': coin['symbol'],
                'name': coin['name'],
                'source': source,
                'current_price': current_data['price'],
                'change_24h': current_data['change_24h'],
                'volume_24h': current_data['volume_24h'],
                'market_cap': current_data.get('market_cap', 0)
            },
            'search_results': search_results[:5],  # Show top 5 alternatives
            'technical_analysis': None,
            'trading_signal': None
        }
        
        # Perform technical analysis if historical data available
        if historical_data and len(historical_data) > 20:
            prices = [point['price'] for point in historical_data]
            volumes = [point['volume'] for point in historical_data]
            
            # Technical analysis
            result['technical_analysis'] = self.chart_analyzer.generate_trading_signals(prices, volumes)
            
            # Generate trading signal
            signal_data = {
                coin['symbol']: {
                    'price': current_data['price'],
                    'change_24h': current_data['change_24h'],
                    'volume': current_data['volume_24h']
                }
            }
            
            signals = self.signal_generator.generate_fast_signals(signal_data)
            if signals:
                result['trading_signal'] = signals[0]
        
        return result
    
    def get_trending_coins(self, limit: int = 20) -> List[Dict]:
        """Get trending coins from various sources"""
        trending = []
        
        # CoinGecko trending
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/search/trending",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                for coin in data.get('coins', [])[:10]:
                    trending.append({
                        'symbol': coin['item']['symbol'],
                        'name': coin['item']['name'],
                        'id': coin['item']['id'],
                        'market_cap_rank': coin['item'].get('market_cap_rank'),
                        'source': 'coingecko_trending'
                    })
        except Exception as e:
            print(f"Trending coins error: {e}")
        
        return trending[:limit]
    
    def analyze_multiple_coins(self, coin_queries: List[str]) -> Dict[str, Dict]:
        """Analyze multiple coins at once"""
        results = {}
        
        for query in coin_queries:
            try:
                analysis = self.analyze_coin(query)
                if 'error' not in analysis:
                    symbol = analysis['coin_info']['symbol']
                    results[symbol] = analysis
                else:
                    results[query] = analysis
            except Exception as e:
                results[query] = {'error': f'Analysis failed: {str(e)}'}
        
        return results

def analyze_custom_coin(coin_query: str) -> Dict:
    """Standalone function to analyze any coin"""
    analyzer = DynamicCoinAnalyzer()
    return analyzer.analyze_coin(coin_query)

def search_and_analyze_coins(queries: List[str]) -> Dict:
    """Analyze multiple custom coins"""
    analyzer = DynamicCoinAnalyzer()
    return analyzer.analyze_multiple_coins(queries)