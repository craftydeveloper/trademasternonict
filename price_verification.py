"""
Price Verification System
Checks current real market prices from multiple sources
"""

import requests
import json
from datetime import datetime

def get_real_sol_price():
    """Get real SOL price from multiple sources"""
    
    sources = []
    
    # Try CoinGecko
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'solana' in data and 'usd' in data['solana']:
                price = data['solana']['usd']
                sources.append(('CoinGecko', price))
    except Exception as e:
        print(f"CoinGecko error: {e}")
    
    # Try CoinCap
    try:
        response = requests.get("https://api.coincap.io/v2/assets/solana", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'priceUsd' in data['data']:
                price = float(data['data']['priceUsd'])
                sources.append(('CoinCap', price))
    except Exception as e:
        print(f"CoinCap error: {e}")
    
    # Try CryptoCompare
    try:
        response = requests.get("https://min-api.cryptocompare.com/data/price?fsym=SOL&tsyms=USD", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'USD' in data:
                price = data['USD']
                sources.append(('CryptoCompare', price))
    except Exception as e:
        print(f"CryptoCompare error: {e}")
    
    return sources

def get_multiple_crypto_prices():
    """Get current prices for multiple cryptocurrencies"""
    
    # Try CoinCap for multiple assets
    try:
        response = requests.get("https://api.coincap.io/v2/assets?ids=solana,chainlink,avalanche-2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            prices = {}
            if 'data' in data:
                for asset in data['data']:
                    symbol = asset['symbol']
                    price = float(asset['priceUsd'])
                    prices[symbol] = price
            return prices
    except Exception as e:
        print(f"Multiple price fetch error: {e}")
    
    return {}

if __name__ == "__main__":
    print("=== REAL MARKET PRICE VERIFICATION ===")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check SOL specifically
    sol_sources = get_real_sol_price()
    if sol_sources:
        print("SOL PRICE SOURCES:")
        for source, price in sol_sources:
            print(f"• {source}: ${price:.2f}")
        
        # Calculate average if multiple sources
        if len(sol_sources) > 1:
            avg_price = sum(price for _, price in sol_sources) / len(sol_sources)
            print(f"• Average: ${avg_price:.2f}")
    else:
        print("Unable to fetch SOL price from any source")
    
    print()
    
    # Check multiple cryptos
    multi_prices = get_multiple_crypto_prices()
    if multi_prices:
        print("CURRENT MARKET PRICES:")
        for symbol, price in multi_prices.items():
            print(f"• {symbol}: ${price:.2f}")
    
    print()
    print("Note: These are real-time market prices for trading verification")