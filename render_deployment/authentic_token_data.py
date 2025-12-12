"""
Authentic Token Data Handler
Manages real market data for supported trading pairs only
"""
import requests
import time
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class AuthenticTokenDataHandler:
    """Handles authentic data for confirmed supported tokens"""
    
    def __init__(self):
        # Core tokens with guaranteed authentic data sources
        self.core_tokens = {
            'BTC': {'coingecko_id': 'bitcoin', 'reliable': True},
            'ETH': {'coingecko_id': 'ethereum', 'reliable': True},
            'SOL': {'coingecko_id': 'solana', 'reliable': True},
            'ADA': {'coingecko_id': 'cardano', 'reliable': True},
            'DOT': {'coingecko_id': 'polkadot', 'reliable': True},
            'MATIC': {'coingecko_id': 'matic-network', 'reliable': True},
            'AVAX': {'coingecko_id': 'avalanche-2', 'reliable': True},
            'LINK': {'coingecko_id': 'chainlink', 'reliable': True}
        }
        
        # Extended tokens - available but may have data limitations
        self.extended_tokens = {
            'AXS': {'coingecko_id': 'axie-infinity', 'reliable': False},
            'SAND': {'coingecko_id': 'the-sandbox', 'reliable': False},
            'MANA': {'coingecko_id': 'decentraland', 'reliable': False},
            'UNI': {'coingecko_id': 'uniswap', 'reliable': False},
            'AAVE': {'coingecko_id': 'aave', 'reliable': False},
            'PEPE': {'coingecko_id': 'pepe', 'reliable': False},
            'BNB': {'coingecko_id': 'binancecoin', 'reliable': False},
            'XRP': {'coingecko_id': 'ripple', 'reliable': False},
            'DOGE': {'coingecko_id': 'dogecoin', 'reliable': False},
            'SHIB': {'coingecko_id': 'shiba-inu', 'reliable': False},
            'LTC': {'coingecko_id': 'litecoin', 'reliable': False},
            'BCH': {'coingecko_id': 'bitcoin-cash', 'reliable': False},
            'ATOM': {'coingecko_id': 'cosmos', 'reliable': False},
            'ICP': {'coingecko_id': 'internet-computer', 'reliable': False},
            'NEAR': {'coingecko_id': 'near', 'reliable': False},
            'APT': {'coingecko_id': 'aptos', 'reliable': False},
            'ARB': {'coingecko_id': 'arbitrum', 'reliable': False},
            'OP': {'coingecko_id': 'optimism', 'reliable': False},
            'FTM': {'coingecko_id': 'fantom', 'reliable': False},
            'ALGO': {'coingecko_id': 'algorand', 'reliable': False},
            'VET': {'coingecko_id': 'vechain', 'reliable': False},
            'HBAR': {'coingecko_id': 'hedera-hashgraph', 'reliable': False},
            'FIL': {'coingecko_id': 'filecoin', 'reliable': False},
            'EOS': {'coingecko_id': 'eos', 'reliable': False},
            'XTZ': {'coingecko_id': 'tezos', 'reliable': False},
            'EGLD': {'coingecko_id': 'elrond-erd-2', 'reliable': False},
            'FLOW': {'coingecko_id': 'flow', 'reliable': False},
            'KAS': {'coingecko_id': 'kaspa', 'reliable': False},
            'GALA': {'coingecko_id': 'gala', 'reliable': False},
            'ENJ': {'coingecko_id': 'enjincoin', 'reliable': False},
            'IMX': {'coingecko_id': 'immutable-x', 'reliable': False},
            'FET': {'coingecko_id': 'fetch-ai', 'reliable': False},
            'AGIX': {'coingecko_id': 'singularitynet', 'reliable': False},
            'OCEAN': {'coingecko_id': 'ocean-protocol', 'reliable': False},
            'GRT': {'coingecko_id': 'the-graph', 'reliable': False},
            'RNDR': {'coingecko_id': 'render-token', 'reliable': False}
        }
        
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # Stricter rate limiting
    
    def is_token_supported(self, symbol: str) -> tuple[bool, bool]:
        """Check if token is supported and if it's reliable"""
        if symbol in self.core_tokens:
            return True, True
        elif symbol in self.extended_tokens:
            return True, False
        else:
            return False, False
    
    def get_token_data(self, symbol: str) -> Optional[Dict]:
        """Get authentic token data with proper rate limiting"""
        supported, reliable = self.is_token_supported(symbol)
        
        if not supported:
            return None
        
        # Use appropriate token mapping
        token_info = self.core_tokens.get(symbol, self.extended_tokens.get(symbol))
        if not token_info:
            return None
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': token_info['coingecko_id'],
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                token_data = data.get(token_info['coingecko_id'], {})
                
                if token_data:
                    return {
                        'price': token_data.get('usd', 0),
                        'price_change_24h': token_data.get('usd_24h_change', 0),
                        'volume_24h': token_data.get('usd_24h_vol', 0),
                        'reliable': reliable,
                        'source': 'coingecko'
                    }
            
            logger.warning(f"Failed to fetch data for {symbol}: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def get_supported_tokens(self) -> List[str]:
        """Get list of all supported tokens"""
        return list(self.core_tokens.keys()) + list(self.extended_tokens.keys())
    
    def get_core_tokens(self) -> List[str]:
        """Get list of core reliable tokens"""
        return list(self.core_tokens.keys())

# Global instance
authentic_data_handler = AuthenticTokenDataHandler()