"""
Monthly Income Calculator
Calculates required capital for target monthly income from trading
"""

import logging

logger = logging.getLogger(__name__)

class MonthlyIncomeCalculator:
    """Calculate capital requirements for consistent monthly income"""
    
    def __init__(self, target_monthly_income: float = 500.0):
        self.target_monthly_income = target_monthly_income
        
    def calculate_capital_requirements(self) -> dict:
        """Calculate required capital for different monthly return scenarios"""
        
        # Different monthly return rates (realistic to aggressive)
        monthly_return_rates = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]  # 5% to 40%
        
        scenarios = {}
        
        for rate in monthly_return_rates:
            required_capital = self.target_monthly_income / rate
            
            scenarios[f"{rate*100:.0f}%_monthly"] = {
                'monthly_return': f"{rate*100:.0f}%",
                'required_capital': f"${required_capital:,.2f}",
                'monthly_income': f"${self.target_monthly_income:.2f}",
                'difficulty_level': self._assess_difficulty(rate),
                'risk_level': self._assess_risk_level(rate),
                'sustainability': self._assess_sustainability(rate)
            }
        
        return scenarios
    
    def calculate_progressive_capital_building(self) -> dict:
        """Calculate how to build capital progressively to reach income target"""
        
        # Starting from different capital levels
        starting_capitals = [500, 1000, 2000, 3000, 5000]
        
        capital_paths = {}
        
        for start_capital in starting_capitals:
            # Assume 20% monthly growth (aggressive but achievable)
            monthly_growth = 0.20
            
            current_capital = start_capital
            months_to_target = 0
            monthly_progression = []
            
            while current_capital * 0.15 < self.target_monthly_income and months_to_target < 24:  # 15% sustainable return
                monthly_profit = current_capital * monthly_growth
                current_capital += monthly_profit
                months_to_target += 1
                
                if months_to_target <= 12:  # Show first year progression
                    monthly_progression.append({
                        'month': months_to_target,
                        'capital': f"${current_capital:,.2f}",
                        'potential_income': f"${current_capital * 0.15:,.2f}"
                    })
            
            # Final sustainable income at 15% monthly return
            sustainable_income = current_capital * 0.15
            
            capital_paths[f"start_{start_capital}"] = {
                'starting_capital': f"${start_capital:,.2f}",
                'months_to_target': months_to_target if months_to_target <= 24 else "More than 2 years",
                'final_capital': f"${current_capital:,.2f}",
                'monthly_income_achieved': f"${sustainable_income:,.2f}",
                'progression': monthly_progression[:6]  # Show first 6 months
            }
        
        return capital_paths
    
    def calculate_leverage_scenarios(self) -> dict:
        """Calculate how leverage affects capital requirements"""
        
        # Base scenario: 10% monthly return without leverage
        base_return = 0.10
        base_capital_needed = self.target_monthly_income / base_return
        
        leverage_scenarios = {}
        
        # Different leverage levels
        leverage_levels = [1, 2, 3, 5, 8, 10, 15, 20]
        
        for leverage in leverage_levels:
            # With leverage, effective return increases but so does risk
            effective_return = base_return * leverage
            required_capital = self.target_monthly_income / effective_return
            
            # Calculate risk metrics
            potential_loss_per_month = required_capital * effective_return  # Could lose entire monthly profit
            margin_requirement = required_capital  # Assuming 1:1 margin for simplicity
            
            leverage_scenarios[f"{leverage}x_leverage"] = {
                'leverage': f"{leverage}x",
                'required_capital': f"${required_capital:,.2f}",
                'effective_monthly_return': f"{effective_return*100:.0f}%",
                'risk_level': self._assess_leverage_risk(leverage),
                'potential_monthly_loss': f"${potential_loss_per_month:,.2f}",
                'margin_requirement': f"${margin_requirement:,.2f}"
            }
        
        return leverage_scenarios
    
    def calculate_realistic_income_ladder(self) -> dict:
        """Calculate realistic income progression ladder"""
        
        # Progressive income targets
        income_targets = [100, 200, 300, 400, 500, 750, 1000, 1500, 2000]
        
        ladder = {}
        
        for target in income_targets:
            # Using 15% monthly return (aggressive but sustainable)
            sustainable_return = 0.15
            required_capital = target / sustainable_return
            
            # Using 25% monthly return (very aggressive)
            aggressive_return = 0.25
            aggressive_capital = target / aggressive_return
            
            ladder[f"target_{target}"] = {
                'monthly_target': f"${target:.2f}",
                'conservative_capital': f"${required_capital:,.2f} (15% monthly)",
                'aggressive_capital': f"${aggressive_capital:,.2f} (25% monthly)",
                'months_to_build_from_1k': self._months_to_build_capital(1000, required_capital),
                'difficulty': 'Moderate' if target <= 500 else 'High' if target <= 1000 else 'Very High'
            }
        
        return ladder
    
    def _assess_difficulty(self, monthly_return: float) -> str:
        """Assess difficulty of achieving monthly return"""
        if monthly_return <= 0.10:
            return "Moderate - Achievable with good strategy"
        elif monthly_return <= 0.20:
            return "High - Requires skill and favorable conditions"
        elif monthly_return <= 0.30:
            return "Very High - Professional level trading required"
        else:
            return "Extreme - Nearly impossible to sustain"
    
    def _assess_risk_level(self, monthly_return: float) -> str:
        """Assess risk level for monthly return target"""
        if monthly_return <= 0.10:
            return "Moderate Risk"
        elif monthly_return <= 0.20:
            return "High Risk"
        elif monthly_return <= 0.30:
            return "Very High Risk"
        else:
            return "Extreme Risk"
    
    def _assess_sustainability(self, monthly_return: float) -> str:
        """Assess sustainability of monthly return"""
        if monthly_return <= 0.10:
            return "Highly Sustainable"
        elif monthly_return <= 0.15:
            return "Sustainable with discipline"
        elif monthly_return <= 0.25:
            return "Difficult to sustain long-term"
        else:
            return "Not sustainable"
    
    def _assess_leverage_risk(self, leverage: int) -> str:
        """Assess risk level of leverage"""
        if leverage <= 2:
            return "Low Risk"
        elif leverage <= 5:
            return "Moderate Risk"
        elif leverage <= 10:
            return "High Risk"
        else:
            return "Extreme Risk"
    
    def _months_to_build_capital(self, start_capital: float, target_capital: float) -> str:
        """Calculate months needed to build capital"""
        if start_capital >= target_capital:
            return "Already achieved"
        
        # Assume 20% monthly growth
        monthly_growth = 0.20
        current = start_capital
        months = 0
        
        while current < target_capital and months < 36:
            current *= 1.20
            months += 1
        
        return f"{months} months" if months <= 36 else "More than 3 years"

def generate_income_analysis(target_income: float = 500.0) -> dict:
    """Generate comprehensive income analysis"""
    
    calculator = MonthlyIncomeCalculator(target_income)
    
    capital_requirements = calculator.calculate_capital_requirements()
    progressive_building = calculator.calculate_progressive_capital_building()
    leverage_scenarios = calculator.calculate_leverage_scenarios()
    income_ladder = calculator.calculate_realistic_income_ladder()
    
    # Find most realistic scenarios
    realistic_options = {}
    for key, scenario in capital_requirements.items():
        if 'Moderate' in scenario['difficulty_level'] or 'High -' in scenario['difficulty_level']:
            realistic_options[key] = scenario
    
    return {
        'target_income': f"${target_income:.2f}",
        'capital_requirements': capital_requirements,
        'realistic_options': realistic_options,
        'progressive_building': progressive_building,
        'leverage_scenarios': leverage_scenarios,
        'income_ladder': income_ladder,
        'recommendations': {
            'conservative_approach': f"${target_income / 0.10:,.2f} capital at 10% monthly return",
            'balanced_approach': f"${target_income / 0.15:,.2f} capital at 15% monthly return",
            'aggressive_approach': f"${target_income / 0.25:,.2f} capital at 25% monthly return",
            'best_strategy': "Build capital progressively while improving trading skills"
        }
    }

if __name__ == "__main__":
    analysis = generate_income_analysis(500.0)
    print(f"Capital Requirements for {analysis['target_income']} Monthly Income:")
    print()
    
    recommendations = analysis['recommendations']
    print("RECOMMENDED APPROACHES:")
    print(f"Conservative: {recommendations['conservative_approach']}")
    print(f"Balanced: {recommendations['balanced_approach']}")
    print(f"Aggressive: {recommendations['aggressive_approach']}")
    print(f"Strategy: {recommendations['best_strategy']}")