#!/usr/bin/env python3
"""
Direct Bybit SOL Price Fetcher
Gets authentic SOL/USDT price from Bybit futures API
"""

import requests
import json

def get_authentic_sol_price():
    """Get authentic SOL price from Bybit futures"""
    try:
        # Bybit public API endpoint for SOL futures
        url = "https://api.bybit.com/v5/market/tickers"
        params = {
            'category': 'linear',
            'symbol': 'SOLUSDT'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                sol_data = data['result']['list'][0]
                price = float(sol_data['lastPrice'])
                volume = float(sol_data['volume24h'])
                change = float(sol_data['price24hPcnt']) * 100
                
                print(f"SOL/USDT Price: ${price:.4f}")
                print(f"24h Volume: {volume:,.0f} SOL")
                print(f"24h Change: {change:+.2f}%")
                print(f"High 24h: ${float(sol_data['highPrice24h']):.4f}")
                print(f"Low 24h: ${float(sol_data['lowPrice24h']):.4f}")
                
                return price
            else:
                print("No SOL data found in response")
                return None
                
        else:
            print(f"API request failed with status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching SOL price: {e}")
        return None

if __name__ == "__main__":
    print("Fetching authentic SOL price from Bybit...")
    price = get_authentic_sol_price()
    
    if price:
        print(f"\n✓ Authentic Bybit SOL Price: ${price:.4f}")
    else:
        print("\n✗ Failed to fetch authentic Bybit price")