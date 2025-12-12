"""
Authenticated Bybit API Client
Gets real-time SOL price directly from Bybit using API credentials
"""
import os
import time
import hashlib
import hmac
import requests
from typing import Optional, Dict

class AuthenticatedBybitClient:
    """Authenticated Bybit API client for real-time price data"""
    
    def __init__(self):
        self.api_key = os.environ.get("BYBIT_API_KEY")
        self.api_secret = os.environ.get("BYBIT_SECRET_KEY")
        self.base_url = "https://api.bybit.com"
        
    def _generate_signature(self, timestamp: str, params: str) -> str:
        """Generate HMAC signature for authenticated requests"""
        param_str = timestamp + self.api_key + "5000" + params
        return hmac.new(
            bytes(self.api_secret, "utf-8"),
            param_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    
    def get_sol_price(self) -> Optional[float]:
        """Get authentic SOL price from Bybit using authenticated API"""
        try:
            if not self.api_key or not self.api_secret:
                print("❌ API credentials not found")
                return None
                
            timestamp = str(int(time.time() * 1000))
            params = "category=linear&symbol=SOLUSDT"
            signature = self._generate_signature(timestamp, params)
            
            headers = {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-SIGN": signature,
                "X-BAPI-SIGN-TYPE": "2",
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": "5000",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/v5/market/tickers?{params}"
            
            print("🔑 Making authenticated request to Bybit...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                    sol_data = data["result"]["list"][0]
                    price = float(sol_data["lastPrice"])
                    print(f"✅ Authentic Bybit SOL price: ${price}")
                    return price
                else:
                    print(f"❌ API error: {data.get('retMsg', 'Unknown error')}")
                    return None
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching SOL price: {e}")
            return None
    
    def get_all_futures_prices(self) -> Optional[Dict[str, float]]:
        """Get all USDT futures prices from Bybit"""
        try:
            if not self.api_key or not self.api_secret:
                return None
                
            timestamp = str(int(time.time() * 1000))
            params = "category=linear"
            signature = self._generate_signature(timestamp, params)
            
            headers = {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-SIGN": signature,
                "X-BAPI-SIGN-TYPE": "2",
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": "5000",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/v5/market/tickers?{params}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("retCode") == 0:
                    prices = {}
                    for item in data.get("result", {}).get("list", []):
                        symbol = item["symbol"]
                        if symbol.endswith("USDT"):
                            base_symbol = symbol.replace("USDT", "")
                            prices[base_symbol] = float(item["lastPrice"])
                    
                    print(f"✅ Retrieved {len(prices)} authentic Bybit prices")
                    return prices
                    
            print(f"❌ Failed to get Bybit prices: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching Bybit prices: {e}")
            return None

def get_authentic_sol_price() -> Optional[float]:
    """Get authentic SOL price from Bybit"""
    client = AuthenticatedBybitClient()
    return client.get_sol_price()

def get_authentic_bybit_prices() -> Optional[Dict[str, float]]:
    """Get all authentic Bybit futures prices"""
    client = AuthenticatedBybitClient()
    return client.get_all_futures_prices()

if __name__ == "__main__":
    print("🚀 Testing authenticated Bybit API access...")
    price = get_authentic_sol_price()
    if price:
        print(f"💰 Current authentic SOL price: ${price}")
    else:
        print("❌ Failed to get authentic SOL price")