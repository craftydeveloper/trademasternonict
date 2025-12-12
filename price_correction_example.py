#!/usr/bin/env python3
"""
Price Correction Management Example
Shows how to use the manual price override system
"""

import sys
from manual_price_override import (
    add_price_correction, 
    remove_price_correction, 
    list_price_corrections,
    update_multiple_corrections
)

def show_current_corrections():
    """Show all current price corrections"""
    corrections = list_price_corrections()
    print(f"\nCurrent Price Corrections ({len(corrections)} total):")
    if corrections:
        for symbol, price in corrections.items():
            print(f"  {symbol}: ${price}")
    else:
        print("  No price corrections active")

def add_correction_example():
    """Example: Add price corrections for multiple tokens"""
    print("\n=== Adding Price Corrections ===")
    
    # Example corrections based on your Bybit platform
    corrections = {
        "BTC": 108500.0,   # If BTC shows $108,500 on Bybit
        "ETH": 2450.0,     # If ETH shows $2,450 on Bybit
        "SOL": 157.0,      # If SOL shows $157 on Bybit
        "DOT": 3.42,       # If DOT shows $3.42 on Bybit
    }
    
    print("Adding corrections for:")
    for symbol, price in corrections.items():
        print(f"  {symbol}: ${price}")
        add_price_correction(symbol, price)

def remove_correction_example():
    """Example: Remove a price correction"""
    print("\n=== Removing Price Correction ===")
    symbol = "BTC"
    print(f"Removing correction for {symbol}")
    remove_price_correction(symbol)

def batch_update_example():
    """Example: Update multiple corrections at once"""
    print("\n=== Batch Update Example ===")
    
    new_corrections = {
        "AVAX": 18.0,
        "LINK": 13.4,
        "UNI": 7.056,  # Keep the UNI correction
    }
    
    print("Batch updating:")
    for symbol, price in new_corrections.items():
        print(f"  {symbol}: ${price}")
    
    update_multiple_corrections(new_corrections)

def main():
    """Main demonstration"""
    print("Price Correction System Demo")
    print("=" * 40)
    
    # Show initial state
    show_current_corrections()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "add":
            add_correction_example()
        elif command == "remove":
            remove_correction_example()
        elif command == "batch":
            batch_update_example()
        elif command == "show":
            pass  # Already shown above
        else:
            print(f"\nUnknown command: {command}")
            print("Usage: python price_correction_example.py [add|remove|batch|show]")
    else:
        print("\nUsage examples:")
        print("  python price_correction_example.py show    # Show current corrections")
        print("  python price_correction_example.py add     # Add example corrections")
        print("  python price_correction_example.py remove  # Remove a correction")
        print("  python price_correction_example.py batch   # Batch update corrections")
    
    # Show final state
    show_current_corrections()
    
    print("\nTo apply corrections to live trading:")
    print("1. Check your Bybit platform for exact prices")
    print("2. Add corrections using add_price_correction(symbol, price)")
    print("3. Corrections are applied automatically in signal generation")
    print("4. Use the API endpoints for web-based management")

if __name__ == "__main__":
    main()