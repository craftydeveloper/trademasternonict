"""
Live Price Simulator - Simulates Real-time Price Movements
Creates continuous price variations like Bybit futures for live trading feel
"""
import random
import time
from typing import Dict, Optional
from live_bybit_sync import get_live_bybit_prices

class LivePriceSimulator:
    """Simulates live price movements with realistic variations"""
    
    def __init__(self):
        self.base_prices = {}
        self.last_update = time.time()
        self.price_directions = {}  # Track if price is trending up/down
        
    def get_live_prices(self) -> Dict[str, float]:
        """Get simulated live prices with realistic movement"""
        try:
            current_time = time.time()
            
            # Get base prices from Bybit every 30 seconds
            if not self.base_prices or (current_time - self.last_update) > 30:
                self.base_prices = get_live_bybit_prices()
                self.last_update = current_time
                print(f"Updated base prices from Bybit: {len(self.base_prices)} tokens")
            
            # Apply realistic live variations
            live_prices = {}
            for symbol, base_price in self.base_prices.items():
                # Create realistic price movement (±0.1% to ±0.3%)
                variation_percent = random.uniform(-0.003, 0.003)  # ±0.3%
                
                # Add momentum - prices tend to continue in same direction
                if symbol in self.price_directions:
                    momentum = self.price_directions[symbol] * 0.5
                    variation_percent += momentum * random.uniform(0, 0.001)
                
                # Calculate new price
                new_price = base_price * (1 + variation_percent)
                
                # Store direction for momentum
                if symbol in live_prices:
                    if new_price > live_prices[symbol]:
                        self.price_directions[symbol] = 1  # Up trend
                    elif new_price < live_prices[symbol]:
                        self.price_directions[symbol] = -1  # Down trend
                else:
                    self.price_directions[symbol] = random.choice([-1, 1])
                
                # Ensure reasonable precision
                if new_price > 1:
                    live_prices[symbol] = round(new_price, 2)
                elif new_price > 0.01:
                    live_prices[symbol] = round(new_price, 4)
                else:
                    live_prices[symbol] = round(new_price, 6)
            
            return live_prices
            
        except Exception as e:
            print(f"Live price simulation error: {e}")
            # Return base prices if simulation fails
            return self.base_prices if self.base_prices else {}

# Global instance
live_simulator = LivePriceSimulator()

def get_simulated_live_prices() -> Dict[str, float]:
    """Get live simulated prices with movement"""
    return live_simulator.get_live_prices()