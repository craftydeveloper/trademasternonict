"""
Manual Price Override System
Corrects specific price discrepancies between Bybit platform and trading bot
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Manual price corrections based on actual Bybit platform values
# Update these prices to match your current Bybit platform exactly
MANUAL_PRICE_CORRECTIONS = {
    "UNI": 7.056,  # Corrected from $7.23 to actual Bybit price $7.056
    # "BTC": 108500.0,  # Example: Add BTC correction if needed
    # "ETH": 2450.0,    # Example: Add ETH correction if needed  
    # "SOL": 157.0,     # Example: Add SOL correction if needed
    # "DOT": 3.42,      # Example: Add DOT correction if needed
    # "AVAX": 18.0,     # Example: Add AVAX correction if needed
    # "LINK": 13.4,     # Example: Add LINK correction if needed
}

def apply_manual_price_corrections(prices: Dict[str, float]) -> Dict[str, float]:
    """Apply manual price corrections for known discrepancies"""
    corrected_prices = prices.copy()
    
    corrections_applied = 0
    for symbol, correct_price in MANUAL_PRICE_CORRECTIONS.items():
        if symbol in corrected_prices:
            old_price = corrected_prices[symbol]
            corrected_prices[symbol] = correct_price
            logger.info(f"Price corrected: {symbol} ${old_price:.3f} → ${correct_price:.3f}")
            corrections_applied += 1
    
    if corrections_applied > 0:
        logger.info(f"Applied {corrections_applied} manual price corrections")
    
    return corrected_prices

def get_corrected_price(symbol: str, fallback_price: float) -> float:
    """Get corrected price for a symbol, or fallback if no correction needed"""
    return MANUAL_PRICE_CORRECTIONS.get(symbol, fallback_price)

def add_price_correction(symbol: str, bybit_price: float):
    """Add a new price correction for a token"""
    global MANUAL_PRICE_CORRECTIONS
    MANUAL_PRICE_CORRECTIONS[symbol] = bybit_price
    logger.info(f"Added price correction: {symbol} = ${bybit_price}")

def remove_price_correction(symbol: str):
    """Remove a price correction for a token"""
    global MANUAL_PRICE_CORRECTIONS
    if symbol in MANUAL_PRICE_CORRECTIONS:
        del MANUAL_PRICE_CORRECTIONS[symbol]
        logger.info(f"Removed price correction for {symbol}")

def list_price_corrections() -> Dict[str, float]:
    """Get all current price corrections"""
    return MANUAL_PRICE_CORRECTIONS.copy()

def update_multiple_corrections(corrections: Dict[str, float]):
    """Update multiple price corrections at once"""
    global MANUAL_PRICE_CORRECTIONS
    MANUAL_PRICE_CORRECTIONS.update(corrections)
    logger.info(f"Updated {len(corrections)} price corrections")