"""
Fast Trading Signals Cache
High-performance caching system to eliminate slow API loading
"""
import time
import json
from typing import Dict, List, Optional

class FastSignalsCache:
    """Ultra-fast in-memory cache for trading signals"""
    
    def __init__(self, cache_duration: int = 30):
        self.cache_duration = cache_duration  # 30 seconds
        self.signals_cache = None
        self.cache_timestamp = 0
        self.market_data_cache = None
        self.market_cache_timestamp = 0
    
    def is_cache_valid(self) -> bool:
        """Check if cached signals are still valid"""
        return (self.signals_cache is not None and 
                time.time() - self.cache_timestamp < self.cache_duration)
    
    def is_market_cache_valid(self) -> bool:
        """Check if cached market data is still valid"""
        return (self.market_data_cache is not None and 
                time.time() - self.market_cache_timestamp < 60)  # 1 minute for market data
    
    def get_cached_signals(self) -> Optional[Dict]:
        """Get cached trading signals if valid"""
        if self.is_cache_valid():
            return {
                'signals': self.signals_cache,
                'count': len(self.signals_cache) if self.signals_cache else 0,
                'scan_info': 'Fast cached analysis',
                'cached': True,
                'cache_age': time.time() - self.cache_timestamp
            }
        return None
    
    def cache_signals(self, signals: List[Dict]) -> None:
        """Cache trading signals with timestamp"""
        self.signals_cache = signals
        self.cache_timestamp = time.time()
    
    def get_cached_market_data(self) -> Optional[Dict]:
        """Get cached market data if valid"""
        if self.is_market_cache_valid():
            return self.market_data_cache
        return None
    
    def cache_market_data(self, market_data: Dict) -> None:
        """Cache market data with timestamp"""
        self.market_data_cache = market_data
        self.market_cache_timestamp = time.time()
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.signals_cache = None
        self.cache_timestamp = 0
        self.market_data_cache = None
        self.market_cache_timestamp = 0
    
    def get_cache_status(self) -> Dict:
        """Get cache status information"""
        return {
            'signals_cached': self.signals_cache is not None,
            'signals_valid': self.is_cache_valid(),
            'signals_age': time.time() - self.cache_timestamp if self.cache_timestamp > 0 else 0,
            'market_cached': self.market_data_cache is not None,
            'market_valid': self.is_market_cache_valid(),
            'market_age': time.time() - self.market_cache_timestamp if self.market_cache_timestamp > 0 else 0
        }

# Global cache instance
fast_cache = FastSignalsCache()

def get_fast_signals() -> Optional[Dict]:
    """Get fast cached signals"""
    return fast_cache.get_cached_signals()

def cache_signals(signals: List[Dict]) -> None:
    """Cache signals for fast retrieval"""
    fast_cache.cache_signals(signals)

def clear_signals_cache() -> None:
    """Clear the signals cache"""
    fast_cache.clear_cache()

def get_cache_info() -> Dict:
    """Get cache status information"""
    return fast_cache.get_cache_status()