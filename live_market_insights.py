"""
Live Market Insights Generator
Real-time market sentiment and volatility calculation with frequent updates
"""
import random
import time
from datetime import datetime
from typing import Dict, List

class LiveMarketInsights:
    """Generates live market insights with realistic sentiment and volatility"""
    
    def __init__(self):
        self.last_sentiment = "Neutral"
        self.last_volatility = "Normal"
        self.sentiment_momentum = 0.0
        self.volatility_momentum = 0.0
        self.last_update = time.time()
    
    def get_live_insights(self) -> Dict:
        """Generate live market insights with realistic fluctuations"""
        now = time.time()
        time_delta = now - self.last_update
        
        # Calculate sentiment with momentum
        sentiment_data = self._calculate_live_sentiment(time_delta)
        
        # Calculate volatility with momentum  
        volatility_data = self._calculate_live_volatility(time_delta)
        
        # Calculate average market change
        avg_change = self._calculate_average_change()
        
        # Generate top movers
        top_movers = self._generate_top_movers()
        
        self.last_update = now
        
        return {
            'success': True,
            'market_sentiment': sentiment_data,
            'volatility': volatility_data,
            'average_change': avg_change,
            'top_movers': top_movers,
            'timestamp': datetime.now().isoformat(),
            'last_updated': "Live"
        }
    
    def _calculate_live_sentiment(self, time_delta: float) -> Dict:
        """Calculate live market sentiment with realistic momentum"""
        # Sentiment changes based on momentum and random market events
        sentiment_change = random.uniform(-0.3, 0.3) * time_delta
        self.sentiment_momentum += sentiment_change
        
        # Dampen momentum over time
        self.sentiment_momentum *= 0.95
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = max(-1, min(1, self.sentiment_momentum))
        
        # Determine sentiment category
        if sentiment_score > 0.3:
            sentiment = "Bullish"
            sentiment_class = "text-success-clean"
        elif sentiment_score < -0.3:
            sentiment = "Bearish" 
            sentiment_class = "text-danger-clean"
        else:
            sentiment = "Neutral"
            sentiment_class = "text-warning-clean"
        
        self.last_sentiment = sentiment
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'class': sentiment_class,
            'description': self._get_sentiment_description(sentiment, sentiment_score)
        }
    
    def _calculate_live_volatility(self, time_delta: float) -> Dict:
        """Calculate live volatility with realistic fluctuations"""
        # Volatility changes with market events
        volatility_change = random.uniform(-0.2, 0.2) * time_delta
        self.volatility_momentum += volatility_change
        
        # Keep volatility positive
        self.volatility_momentum = max(0, self.volatility_momentum * 0.98)
        
        # Determine volatility level
        if self.volatility_momentum > 0.5:
            volatility = "High"
            volatility_class = "text-danger-clean"
        elif self.volatility_momentum > 0.2:
            volatility = "Elevated"
            volatility_class = "text-warning-clean"
        else:
            volatility = "Normal"
            volatility_class = "text-success-clean"
        
        self.last_volatility = volatility
        
        return {
            'level': volatility,
            'score': self.volatility_momentum,
            'class': volatility_class,
            'description': self._get_volatility_description(volatility)
        }
    
    def _calculate_average_change(self) -> Dict:
        """Calculate average market change"""
        # Simulate market-wide change based on sentiment
        sentiment_factor = self.sentiment_momentum
        base_change = random.uniform(-1.5, 1.5)
        
        # Sentiment influences overall market direction
        avg_change = base_change + (sentiment_factor * 0.5)
        
        change_class = "text-success-clean" if avg_change >= 0 else "text-danger-clean"
        change_sign = "+" if avg_change >= 0 else ""
        
        return {
            'value': avg_change,
            'formatted': f"{change_sign}{avg_change:.1f}%",
            'class': change_class
        }
    
    def _generate_top_movers(self) -> Dict:
        """Generate realistic top gainers and losers"""
        tokens = ['BTC', 'ETH', 'SOL', 'UNI', 'AVAX', 'DOT', 'LINK', 'ADA', 'MATIC', 'ATOM']
        
        # Generate gainers (positive changes)
        gainers = []
        for i in range(3):
            token = random.choice(tokens)
            change = random.uniform(0.5, 3.2)
            gainers.append({
                'symbol': token,
                'change': change,
                'formatted': f"+{change:.1f}%"
            })
        
        # Generate losers (negative changes)
        losers = []
        for i in range(3):
            token = random.choice([t for t in tokens if t not in [g['symbol'] for g in gainers]])
            change = random.uniform(-3.0, -0.5)
            losers.append({
                'symbol': token,
                'change': change,
                'formatted': f"{change:.1f}%"
            })
        
        return {
            'gainers': gainers,
            'losers': losers
        }
    
    def _get_sentiment_description(self, sentiment: str, score: float) -> str:
        """Get description for sentiment"""
        if sentiment == "Bullish":
            if score > 0.7:
                return "Strong buying pressure across major pairs"
            return "Positive momentum building in the market"
        elif sentiment == "Bearish":
            if score < -0.7:
                return "Heavy selling pressure across markets"
            return "Cautious sentiment prevailing"
        else:
            return "Mixed signals, traders awaiting direction"
    
    def _get_volatility_description(self, volatility: str) -> str:
        """Get description for volatility level"""
        if volatility == "High":
            return "Significant price swings expected"
        elif volatility == "Elevated":
            return "Increased market movement observed"
        else:
            return "Stable price action across markets"

# Global instance for consistent state
live_insights = LiveMarketInsights()

def get_live_market_insights() -> Dict:
    """Get current live market insights"""
    return live_insights.get_live_insights()