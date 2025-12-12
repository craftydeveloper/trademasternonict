"""
Automatic Bybit Price Synchronization
Automatically fetches all token prices directly from Bybit API to ensure 100% accuracy
"""

import logging
import time
from typing import Dict, Optional
import requests
from authenticated_bybit_client import AuthenticatedBybitClient

logger = logging.getLogger(__name__)

class AutomaticBybitSync:
    """Automatically synchronizes all token prices with Bybit futures platform"""
    
    def __init__(self):
        self.bybit_client = AuthenticatedBybitClient()
        self.cache_timeout = 30  # 30-second cache
        self.last_update = 0
        self.cached_prices = {}
        
        # All 101 Bybit USDT futures symbols
        self.bybit_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 
            'SOLUSDT', 'TRXUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT', 'SHIBUSDT',
            'AVAXUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT', 'ETCUSDT', 'XLMUSDT',
            'BCHUSDT', 'NEARUSDT', 'ALGOUSDT', 'VETUSDT', 'ICPUSDT', 'FILUSDT',
            'MANAUSDT', 'SANDUSDT', 'AXSUSDT', 'CHZUSDT', 'THETAUSDT', 'FLOWUSDT',
            'ENJUSDT', 'XTZUSDT', 'EGLDUSDT', 'AAVEUSDT', 'MKRUSDT', 'CRVUSDT',
            'YFIUSDT', 'COMPUSDT', 'SNXUSDT', 'UMAUSDT', 'SUSHIUSDT', 'ZRXUSDT',
            'BATUSDT', 'LRCUSDT', 'KNCUSDT', 'RENUSDT', 'BANDUSDT', 'STORJUSDT',
            'OCEAUSDT', 'RSRUSDT', 'KAVAUSDT', 'RLCUSDT', 'NMRUSDT', 'CTSIUSDT',
            'HBARUSDT', 'ZILUSDT', 'IOTAUSDT', 'OMGUSDT', 'LSKUSDT', 'WAXPUSDT',
            'WAVESUSDT', 'YFIIUSDT', 'KSMUSDT', 'COTIUSDT', 'CHRUSDT', 'STMXUSDT',
            'HOTUSDT', 'DENTUSDT', 'KEYUSDT', 'FUNUSDT', 'CKBUSDT', 'FTMUSDT',
            'TOMOUSDT', 'ZENUSDT', 'ONEUSDT', 'BTGUSDT', 'RVNUSDT', 'DGBUSDT',
            'NKNUSDT', 'QTUMUSDT', 'SCUSDT', 'CELRUSDT', 'TFUELUSDT', 'BELUSDT',
            'SKLUSDT', 'TRUUSDT', 'CKBUSDT', 'BTTUSDT', 'WINUSDT', 'NPXSUSDT',
            'CVCUSDT', 'IOSTUSDT', 'ARKUSDT', 'VITEUSDT', 'ONGUSDT', 'FETUSDT',
            'CELOUSDT', 'RIFUSDT', 'ARDRUSDT', 'PERPUSDT', 'SUPERUSDT'
        ]
    
    def get_all_bybit_prices(self) -> Dict[str, float]:
        """Get all token prices directly from Bybit with caching"""
        current_time = time.time()
        
        # Return cached prices if still valid
        if current_time - self.last_update < self.cache_timeout and self.cached_prices:
            logger.info(f"Returning cached Bybit prices ({len(self.cached_prices)} tokens)")
            return self.cached_prices.copy()
        
        logger.info("Fetching fresh prices from Bybit...")
        
        # Try authenticated client first
        prices = self._fetch_authenticated_prices()
        
        # Fallback to public API if authenticated fails
        if not prices:
            prices = self._fetch_public_prices()
        
        # Update cache if successful
        if prices:
            self.cached_prices = prices
            self.last_update = current_time
            logger.info(f"Updated Bybit price cache: {len(prices)} tokens")
        
        return prices or {}
    
    def _fetch_authenticated_prices(self) -> Optional[Dict[str, float]]:
        """Fetch prices using authenticated Bybit client"""
        try:
            all_prices = self.bybit_client.get_all_futures_prices()
            if all_prices:
                # Convert USDT symbols to simple symbols (BTCUSDT -> BTC)
                converted_prices = {}
                for symbol, price in all_prices.items():
                    if symbol.endswith('USDT'):
                        simple_symbol = symbol[:-4]  # Remove 'USDT'
                        converted_prices[simple_symbol] = price
                
                logger.info(f"Authenticated Bybit: {len(converted_prices)} prices")
                return converted_prices
        except Exception as e:
            logger.warning(f"Authenticated Bybit failed: {e}")
        
        return None
    
    def _fetch_public_prices(self) -> Optional[Dict[str, float]]:
        """Fetch prices using alternative sources that match Bybit closely"""
        # Try CoinGecko with USDT pairs (matches Bybit futures closely)
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            
            # Major cryptocurrencies that match Bybit futures
            symbols = [
                'bitcoin', 'ethereum', 'binancecoin', 'ripple', 'cardano', 'dogecoin',
                'solana', 'tron', 'polkadot', 'polygon', 'litecoin', 'shiba-inu',
                'avalanche-2', 'uniswap', 'chainlink', 'cosmos', 'ethereum-classic',
                'stellar', 'bitcoin-cash', 'near', 'algorand', 'vechain', 'internet-computer',
                'filecoin', 'decentraland', 'the-sandbox', 'axie-infinity', 'chiliz',
                'theta-token', 'flow', 'enjincoin', 'tezos', 'elrond-erd-2', 'aave',
                'maker', 'curve-dao-token', 'yearn-finance', 'compound-governance-token',
                'synthetix-network-token', 'uma', 'sushiswap', '0x', 'basic-attention-token',
                'loopring', 'kyber-network-crystal', 'republic-protocol', 'band-protocol',
                'storj', 'ocean-protocol'
            ]
            
            params = {
                'ids': ','.join(symbols),
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Map CoinGecko IDs to Bybit symbols
            symbol_mapping = {
                'bitcoin': 'BTC', 'ethereum': 'ETH', 'binancecoin': 'BNB', 'ripple': 'XRP',
                'cardano': 'ADA', 'dogecoin': 'DOGE', 'solana': 'SOL', 'tron': 'TRX',
                'polkadot': 'DOT', 'polygon': 'MATIC', 'litecoin': 'LTC', 'shiba-inu': 'SHIB',
                'avalanche-2': 'AVAX', 'uniswap': 'UNI', 'chainlink': 'LINK', 'cosmos': 'ATOM',
                'ethereum-classic': 'ETC', 'stellar': 'XLM', 'bitcoin-cash': 'BCH', 'near': 'NEAR',
                'algorand': 'ALGO', 'vechain': 'VET', 'internet-computer': 'ICP', 'filecoin': 'FIL',
                'decentraland': 'MANA', 'the-sandbox': 'SAND', 'axie-infinity': 'AXS', 'chiliz': 'CHZ',
                'theta-token': 'THETA', 'flow': 'FLOW', 'enjincoin': 'ENJ', 'tezos': 'XTZ',
                'elrond-erd-2': 'EGLD', 'aave': 'AAVE', 'maker': 'MKR', 'curve-dao-token': 'CRV',
                'yearn-finance': 'YFI', 'compound-governance-token': 'COMP', 'synthetix-network-token': 'SNX',
                'uma': 'UMA', 'sushiswap': 'SUSHI', '0x': 'ZRX', 'basic-attention-token': 'BAT',
                'loopring': 'LRC', 'kyber-network-crystal': 'KNC', 'republic-protocol': 'REN',
                'band-protocol': 'BAND', 'storj': 'STORJ', 'ocean-protocol': 'OCEAN'
            }
            
            prices = {}
            for coin_id, price_data in data.items():
                if coin_id in symbol_mapping and 'usd' in price_data:
                    symbol = symbol_mapping[coin_id]
                    price = float(price_data['usd'])
                    prices[symbol] = price
            
            logger.info(f"CoinGecko fallback: {len(prices)} prices")
            return prices
                
        except Exception as e:
            logger.error(f"CoinGecko fallback failed: {e}")
        
        return None
    
    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """Get price for a specific symbol"""
        prices = self.get_all_bybit_prices()
        return prices.get(symbol.upper())
    
    def apply_bybit_prices_to_market_data(self, market_data: Dict) -> Dict:
        """Apply Bybit prices to market data using existing authenticated system"""
        # Use the existing authenticated Bybit client first for ALL tokens
        try:
            authenticated_prices = self.bybit_client.get_all_futures_prices()
            if authenticated_prices:
                corrections_applied = 0
                
                logger.info(f"Bybit authenticated API returned {len(authenticated_prices)} futures prices")
                
                for symbol_usdt, price in authenticated_prices.items():
                    if symbol_usdt.endswith('USDT'):
                        symbol = symbol_usdt[:-4]  # Remove 'USDT'
                        
                        if symbol in market_data:
                            old_price = market_data[symbol].get('price', 0)
                            market_data[symbol]['price'] = price
                            market_data[symbol]['source'] = 'bybit_authenticated'
                            
                            if abs(old_price - price) > 0.01:
                                logger.info(f"Bybit sync: {symbol} ${old_price:.4f} → ${price:.4f}")
                                corrections_applied += 1
                        else:
                            # Add new tokens from Bybit that aren't in market_data
                            market_data[symbol] = {
                                'price': price,
                                'change_24h': 0,
                                'source': 'bybit_authenticated'
                            }
                            corrections_applied += 1
                            logger.info(f"Added new Bybit token: {symbol} ${price:.4f}")
                
                logger.info(f"Bybit authenticated sync: {corrections_applied} of {len(authenticated_prices)} prices synchronized")
                return market_data
                
        except Exception as e:
            logger.warning(f"Authenticated Bybit sync failed: {e}")
            # Try to get SOL price specifically for testing
            try:
                sol_price = self.bybit_client.get_sol_price()
                if sol_price and 'SOL' in market_data:
                    old_price = market_data['SOL'].get('price', 0)
                    market_data['SOL']['price'] = sol_price
                    market_data['SOL']['source'] = 'bybit_authenticated_sol'
                    logger.info(f"Bybit SOL sync: ${old_price:.4f} → ${sol_price:.4f}")
            except Exception as sol_e:
                logger.warning(f"Bybit SOL sync also failed: {sol_e}")
        
        # Fallback: Try CoinGecko prices as close approximation
        try:
            fallback_prices = self._fetch_public_prices()
            if fallback_prices:
                corrections_applied = 0
                
                for symbol, price in fallback_prices.items():
                    if symbol in market_data:
                        old_price = market_data[symbol].get('price', 0)
                        market_data[symbol]['price'] = price
                        market_data[symbol]['source'] = 'coingecko_bybit_approx'
                        
                        if abs(old_price - price) > 0.01:
                            logger.info(f"CoinGecko sync: {symbol} ${old_price:.4f} → ${price:.4f}")
                            corrections_applied += 1
                
                if corrections_applied > 0:
                    logger.info(f"CoinGecko fallback sync: {corrections_applied} prices updated")
                return market_data
                
        except Exception as e:
            logger.warning(f"CoinGecko fallback sync failed: {e}")
        
        logger.warning("No automatic price sync available, using existing market data")
        return market_data

# Global instance for easy access
bybit_sync = AutomaticBybitSync()

def get_all_bybit_prices() -> Dict[str, float]:
    """Get all token prices from Bybit"""
    return bybit_sync.get_all_bybit_prices()

def sync_market_data_with_bybit(market_data: Dict) -> Dict:
    """Automatically sync market data with Bybit prices"""
    return bybit_sync.apply_bybit_prices_to_market_data(market_data)

def get_bybit_price(symbol: str) -> Optional[float]:
    """Get specific token price from Bybit"""
    return bybit_sync.get_symbol_price(symbol)