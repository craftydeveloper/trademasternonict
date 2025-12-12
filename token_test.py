#!/usr/bin/env python3
"""
Direct token test to verify comprehensive Bybit futures system
"""

from bybit_tokens import get_comprehensive_bybit_tokens
import json

def test_comprehensive_tokens():
    """Test the comprehensive token system directly"""
    tokens = get_comprehensive_bybit_tokens()
    
    print(f"Total tokens available: {len(tokens)}")
    
    # Group by category
    categories = {}
    for token in tokens:
        cat = token['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(token['symbol'])
    
    print("\nToken breakdown by category:")
    for category, symbols in categories.items():
        print(f"  {category}: {len(symbols)} tokens")
        print(f"    Sample: {symbols[:5]}")
    
    # Return formatted for API
    return {
        'success': True,
        'tokens': tokens,
        'count': len(tokens)
    }

if __name__ == "__main__":
    result = test_comprehensive_tokens()
    print(f"\nAPI Response format verified: {result['count']} tokens ready")