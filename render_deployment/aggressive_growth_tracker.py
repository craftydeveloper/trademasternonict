"""
Aggressive Growth Tracker for $50K in 90 Days
Automated tracking, alerts, and optimization system
"""

from datetime import datetime, timedelta
import json
import math

class AggressiveGrowthTracker:
    def __init__(self, starting_balance=500.0, target_amount=50000.0, days=90):
        self.starting_balance = starting_balance
        self.target_amount = target_amount
        self.days = days
        self.start_date = datetime.utcnow()
        self.target_multiple = target_amount / starting_balance
        self.required_daily_rate = (self.target_multiple ** (1/days)) - 1
        
    def calculate_current_progress(self, current_balance):
        """Calculate current progress against target"""
        days_elapsed = max(1, (datetime.utcnow() - self.start_date).days)
        progress_percentage = (current_balance / self.target_amount) * 100
        
        # Calculate actual vs required performance
        actual_multiple = current_balance / self.starting_balance
        required_multiple_today = self.starting_balance * ((1 + self.required_daily_rate) ** days_elapsed)
        
        performance_gap = current_balance - required_multiple_today
        
        return {
            'days_elapsed': days_elapsed,
            'days_remaining': self.days - days_elapsed,
            'current_balance': current_balance,
            'progress_percentage': progress_percentage,
            'required_balance_today': required_multiple_today,
            'performance_gap': performance_gap,
            'on_track': performance_gap >= 0,
            'daily_rate_needed_remaining': self.calculate_adjusted_daily_rate(current_balance, days_elapsed)
        }
    
    def calculate_adjusted_daily_rate(self, current_balance, days_elapsed):
        """Calculate required daily rate for remaining period"""
        days_remaining = max(1, self.days - days_elapsed)
        remaining_multiple = self.target_amount / current_balance
        return (remaining_multiple ** (1/days_remaining)) - 1
    
    def generate_milestone_targets(self):
        """Generate key milestone targets for tracking"""
        milestones = {}
        balance = self.starting_balance
        
        milestone_days = [7, 14, 21, 30, 45, 60, 75, 90]
        
        for day in milestone_days:
            target_balance = self.starting_balance * ((1 + self.required_daily_rate) ** day)
            milestones[f'day_{day}'] = {
                'target_balance': target_balance,
                'target_date': (self.start_date + timedelta(days=day)).strftime('%Y-%m-%d'),
                'required_daily_rate': self.required_daily_rate * 100,
                'milestone_multiple': target_balance / self.starting_balance
            }
        
        return milestones
    
    def assess_performance_status(self, current_balance, days_elapsed):
        """Assess current performance and provide recommendations"""
        progress = self.calculate_current_progress(current_balance)
        
        if progress['on_track']:
            if progress['performance_gap'] > progress['required_balance_today'] * 0.1:
                status = "EXCEEDING_TARGET"
                recommendation = "Consider taking some profits and reducing risk"
            else:
                status = "ON_TRACK" 
                recommendation = "Maintain current strategy and risk levels"
        else:
            gap_percentage = abs(progress['performance_gap']) / progress['required_balance_today']
            if gap_percentage > 0.2:
                status = "SIGNIFICANTLY_BEHIND"
                recommendation = "Increase risk allocation and trade frequency immediately"
            elif gap_percentage > 0.1:
                status = "BEHIND_TARGET"
                recommendation = "Increase leverage and position sizing"
            else:
                status = "SLIGHTLY_BEHIND"
                recommendation = "Minor adjustments to strategy needed"
        
        return {
            'status': status,
            'recommendation': recommendation,
            'urgency_level': self.calculate_urgency_level(progress),
            'suggested_actions': self.generate_action_plan(progress)
        }
    
    def calculate_urgency_level(self, progress):
        """Calculate urgency level based on progress"""
        if progress['days_remaining'] < 30:
            return "CRITICAL"
        elif progress['days_remaining'] < 60:
            return "HIGH"
        elif not progress['on_track']:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_action_plan(self, progress):
        """Generate specific action plan based on current status"""
        actions = []
        
        daily_rate_needed = progress['daily_rate_needed_remaining'] * 100
        
        if daily_rate_needed > 15:
            actions.extend([
                "EXTREME RISK MODE: 15-20% risk per trade",
                "Maximum leverage (20x) on 95%+ confidence signals only",
                "Increase trading frequency to 8-10 trades daily",
                "Consider crypto scalping in addition to swing trades"
            ])
        elif daily_rate_needed > 12:
            actions.extend([
                "HIGH RISK MODE: 10-15% risk per trade", 
                "15-20x leverage on 90%+ confidence signals",
                "6-8 trades daily with tight monitoring",
                "Focus on high-volatility periods"
            ])
        elif daily_rate_needed > 9:
            actions.extend([
                "AGGRESSIVE MODE: 8-12% risk per trade",
                "12-15x leverage on 85%+ confidence signals", 
                "4-6 trades daily",
                "Maintain current aggressive strategy"
            ])
        else:
            actions.extend([
                "STANDARD AGGRESSIVE: 6-10% risk per trade",
                "8-12x leverage on quality signals",
                "3-4 trades daily with discipline"
            ])
        
        return actions
    
    def calculate_probability_assessment(self, current_balance, days_elapsed):
        """Calculate probability of reaching target based on current performance"""
        progress = self.calculate_current_progress(current_balance)
        daily_rate_needed = progress['daily_rate_needed_remaining'] * 100
        
        # Probability assessment based on required daily rate
        if daily_rate_needed < 5:
            probability = "HIGH (70-90%)"
        elif daily_rate_needed < 8:
            probability = "MEDIUM (40-70%)"
        elif daily_rate_needed < 12:
            probability = "LOW (10-40%)"
        elif daily_rate_needed < 15:
            probability = "VERY LOW (2-10%)"
        else:
            probability = "EXTREMELY LOW (<2%)"
        
        return {
            'probability': probability,
            'daily_rate_needed': daily_rate_needed,
            'feasibility_assessment': self.assess_feasibility(daily_rate_needed)
        }
    
    def assess_feasibility(self, daily_rate_needed):
        """Assess feasibility of required daily rate"""
        if daily_rate_needed < 3:
            return "Achievable with disciplined trading"
        elif daily_rate_needed < 6:
            return "Challenging but possible with skill"
        elif daily_rate_needed < 10:
            return "Requires exceptional performance"
        elif daily_rate_needed < 15:
            return "Extremely difficult, maximum risk required"
        else:
            return "Nearly impossible without extreme luck"
    
    def generate_weekly_targets(self, current_balance, days_elapsed):
        """Generate weekly targets for next 4 weeks"""
        weekly_targets = []
        balance = current_balance
        days_remaining = self.days - days_elapsed
        
        progress = self.calculate_current_progress(current_balance)
        weekly_rate = progress['daily_rate_needed_remaining']
        
        for week in range(1, min(5, (days_remaining // 7) + 1)):
            weekly_balance = balance * ((1 + weekly_rate) ** 7)
            weekly_targets.append({
                'week': week,
                'target_balance': weekly_balance,
                'weekly_gain_needed': weekly_balance - balance,
                'daily_rate': weekly_rate * 100
            })
            balance = weekly_balance
        
        return weekly_targets
    
    def get_comprehensive_status(self, current_balance):
        """Get comprehensive status report"""
        days_elapsed = max(1, (datetime.utcnow() - self.start_date).days)
        progress = self.calculate_current_progress(current_balance)
        performance = self.assess_performance_status(current_balance, days_elapsed)
        probability = self.calculate_probability_assessment(current_balance, days_elapsed)
        
        return {
            'target_info': {
                'starting_balance': self.starting_balance,
                'target_amount': self.target_amount,
                'target_multiple': self.target_multiple,
                'original_daily_rate_needed': self.required_daily_rate * 100
            },
            'current_progress': progress,
            'performance_assessment': performance,
            'probability_analysis': probability,
            'milestones': self.generate_milestone_targets(),
            'last_updated': datetime.utcnow().isoformat()
        }

def track_aggressive_growth(current_balance=500.0):
    """Main function to track aggressive growth progress"""
    tracker = AggressiveGrowthTracker()
    return tracker.get_comprehensive_status(current_balance)

if __name__ == "__main__":
    # Test with current balance
    status = track_aggressive_growth(500.0)
    print(json.dumps(status, indent=2, default=str))