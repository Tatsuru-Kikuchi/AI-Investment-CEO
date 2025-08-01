#!/usr/bin/env python3
"""
AI Investment Simulation Engine

Advanced Monte Carlo simulation system for modeling AI adoption scenarios,
market evolution, and policy impact assessment.
"""

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Callable
import json
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class ScenarioType(Enum):
    BASELINE = "baseline"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    POLICY_INTERVENTION = "policy_intervention"
    DISRUPTION = "disruption"

@dataclass
class SimulationParameters:
    """Parameters for AI adoption simulation."""
    time_horizon: int = 6  # years
    num_simulations: int = 1000
    initial_market_size: float = 7.56  # billion USD
    base_growth_rate: float = 0.233  # 23.3% CAGR
    adoption_rates: Dict[str, float] = None
    volatility: float = 0.15
    
    def __post_init__(self):
        if self.adoption_rates is None:
            self.adoption_rates = {
                'sme': 0.16,
                'large': 0.42,
                'overall': 0.29
            }

class AIAdoptionSimulator:
    """
    Monte Carlo simulation engine for AI adoption scenarios.
    """
    
    def __init__(self, parameters: SimulationParameters = None):
        self.params = parameters or SimulationParameters()
        self.results = {}
        self.scenario_data = {}
        
        # Market dynamics parameters
        self.market_drivers = {
            'demographic_pressure': {'weight': 0.25, 'volatility': 0.10},
            'technology_advancement': {'weight': 0.30, 'volatility': 0.20},
            'economic_conditions': {'weight': 0.20, 'volatility': 0.25},
            'government_policy': {'weight': 0.15, 'volatility': 0.15},
            'competitive_pressure': {'weight': 0.10, 'volatility': 0.18}
        }
        
        # Adoption diffusion parameters
        self.diffusion_params = {
            'innovation_coefficient': 0.03,  # p parameter in Bass model
            'imitation_coefficient': 0.38,   # q parameter in Bass model
            'market_potential': 1.0          # Maximum adoption rate
        }
    
    def generate_market_shocks(self, n_years: int, n_simulations: int) -> np.ndarray:
        """
        Generate random market shocks for Monte Carlo simulation.
        
        Args:
            n_years: Number of years to simulate
            n_simulations: Number of simulation runs
            
        Returns:
            Array of market shock multipliers
        """
        # Generate correlated shocks for different market drivers
        shocks = {}
        
        for driver, params in self.market_drivers.items():
            # Generate auto-correlated shocks (economic conditions persist)
            base_shocks = np.random.normal(0, params['volatility'], (n_simulations, n_years))
            
            # Apply auto-correlation
            correlated_shocks = np.zeros_like(base_shocks)
            correlated_shocks[:, 0] = base_shocks[:, 0]
            
            for t in range(1, n_years):
                correlated_shocks[:, t] = (0.7 * correlated_shocks[:, t-1] + 
                                         0.3 * base_shocks[:, t])
            
            shocks[driver] = correlated_shocks
        
        # Combine shocks with weights
        combined_shocks = np.zeros((n_simulations, n_years))
        for driver, shock_array in shocks.items():
            weight = self.market_drivers[driver]['weight']
            combined_shocks += weight * shock_array
        
        # Convert to multiplicative shocks (1 + shock_rate)
        return np.exp(combined_shocks)
    
    def bass_diffusion_model(self, t: float, p: float, q: float, m: float, 
                           current_adopters: float) -> float:
        """
        Bass diffusion model for technology adoption.
        
        Args:
            t: Time period
            p: Innovation coefficient
            q: Imitation coefficient  
            m: Market potential
            current_adopters: Current adoption rate
            
        Returns:
            New adoption rate for the period
        """
        if current_adopters >= m:
            return 0.0
        
        remaining_potential = m - current_adopters
        innovation_effect = p * remaining_potential
        imitation_effect = (q * current_adopters * remaining_potential) / m
        
        return innovation_effect + imitation_effect
    
    def simulate_adoption_scenario(self, scenario_type: ScenarioType, 
                                 policy_effects: Dict[str, float] = None) -> Dict[str, np.ndarray]:
        """
        Simulate AI adoption under specific scenario conditions.
        
        Args:
            scenario_type: Type of scenario to simulate
            policy_effects: Dictionary of policy intervention effects
            
        Returns:
            Dictionary containing simulation results
        """
        n_years = self.params.time_horizon
        n_sims = self.params.num_simulations
        
        # Initialize arrays
        market_size = np.zeros((n_sims, n_years + 1))
        sme_adoption = np.zeros((n_sims, n_years + 1))
        large_adoption = np.zeros((n_sims, n_years + 1))
        overall_adoption = np.zeros((n_sims, n_years + 1))
        
        # Set initial conditions
        market_size[:, 0] = self.params.initial_market_size
        sme_adoption[:, 0] = self.params.adoption_rates['sme']
        large_adoption[:, 0] = self.params.adoption_rates['large']
        overall_adoption[:, 0] = self.params.adoption_rates['overall']
        
        # Generate market shocks
        shocks = self.generate_market_shocks(n_years, n_sims)
        
        # Scenario-specific adjustments
        scenario_multipliers = self._get_scenario_multipliers(scenario_type, policy_effects)
        
        # Run simulation
        for year in range(1, n_years + 1):
            for sim in range(n_sims):
                # Market size evolution
                base_growth = 1 + self.params.base_growth_rate
                shock_effect = shocks[sim, year - 1]
                scenario_effect = scenario_multipliers['market_growth']
                
                market_size[sim, year] = (market_size[sim, year - 1] * 
                                        base_growth * shock_effect * scenario_effect)
                
                # Adoption evolution using Bass diffusion model
                # SME adoption
                sme_growth = self.bass_diffusion_model(
                    year, 
                    self.diffusion_params['innovation_coefficient'] * scenario_multipliers['sme_innovation'],
                    self.diffusion_params['imitation_coefficient'] * scenario_multipliers['sme_imitation'],
                    scenario_multipliers['sme_potential'],
                    sme_adoption[sim, year - 1]
                )
                sme_adoption[sim, year] = min(
                    sme_adoption[sim, year - 1] + sme_growth * shock_effect,
                    scenario_multipliers['sme_potential']
                )
                
                # Large enterprise adoption
                large_growth = self.bass_diffusion_model(
                    year,
                    self.diffusion_params['innovation_coefficient'] * scenario_multipliers['large_innovation'],
                    self.diffusion_params['imitation_coefficient'] * scenario_multipliers['large_imitation'],
                    scenario_multipliers['large_potential'],
                    large_adoption[sim, year - 1]
                )
                large_adoption[sim, year] = min(
                    large_adoption[sim, year - 1] + large_growth * shock_effect,
                    scenario_multipliers['large_potential']
                )
                
                # Overall adoption (weighted average)
                sme_weight = 0.7  # 70% of companies are SMEs
                large_weight = 0.3  # 30% are large enterprises
                overall_adoption[sim, year] = (sme_weight * sme_adoption[sim, year] + 
                                             large_weight * large_adoption[sim, year])
        
        return {
            'market_size': market_size,
            'sme_adoption': sme_adoption,
            'large_adoption': large_adoption,
            'overall_adoption': overall_adoption,
            'years': np.arange(n_years + 1)
        }
    
    def _get_scenario_multipliers(self, scenario_type: ScenarioType, 
                                policy_effects: Dict[str, float] = None) -> Dict[str, float]:
        """
        Get scenario-specific multipliers for simulation parameters.
        
        Args:
            scenario_type: Type of scenario
            policy_effects: Policy intervention effects
            
        Returns:
            Dictionary of multipliers
        """
        base_multipliers = {
            'market_growth': 1.0,
            'sme_innovation': 1.0,
            'sme_imitation': 1.0,
            'sme_potential': 0.8,  # Max 80% adoption for SMEs
            'large_innovation': 1.0,
            'large_imitation': 1.0,
            'large_potential': 0.9  # Max 90% adoption for large enterprises
        }
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            return {
                'market_growth': 1.15,
                'sme_innovation': 1.3,
                'sme_imitation': 1.2,
                'sme_potential': 0.85,
                'large_innovation': 1.2,
                'large_imitation': 1.1,
                'large_potential': 0.95
            }
        
        elif scenario_type == ScenarioType.PESSIMISTIC:
            return {
                'market_growth': 0.85,
                'sme_innovation': 0.7,
                'sme_imitation': 0.8,
                'sme_potential': 0.6,
                'large_innovation': 0.8,
                'large_imitation': 0.9,
                'large_potential': 0.8
            }
        
        elif scenario_type == ScenarioType.POLICY_INTERVENTION:
            policy_multipliers = base_multipliers.copy()
            if policy_effects:
                policy_multipliers['sme_innovation'] *= (1 + policy_effects.get('sme_support', 0))
                policy_multipliers['sme_potential'] += policy_effects.get('sme_support', 0) * 0.3
                policy_multipliers['market_growth'] *= (1 + policy_effects.get('overall_boost', 0))
            return policy_multipliers
        
        elif scenario_type == ScenarioType.DISRUPTION:
            return {
                'market_growth': 1.25,
                'sme_innovation': 0.8,  # Disruption hurts SMEs initially
                'sme_imitation': 1.4,   # But they learn from leaders
                'sme_potential': 0.9,
                'large_innovation': 1.5,  # Large companies lead disruption
                'large_imitation': 1.0,
                'large_potential': 0.95
            }
        
        return base_multipliers
    
    def run_comprehensive_analysis(self) -> Dict[str, Dict]:
        """
        Run comprehensive analysis across multiple scenarios.
        
        Returns:
            Dictionary containing results for all scenarios
        """
        scenarios = [
            (ScenarioType.BASELINE, None),
            (ScenarioType.OPTIMISTIC, None),
            (ScenarioType.PESSIMISTIC, None),
            (ScenarioType.POLICY_INTERVENTION, {'sme_support': 0.15, 'overall_boost': 0.05}),
            (ScenarioType.DISRUPTION, None)
        ]
        
        results = {}
        
        for scenario_type, policy_effects in scenarios:
            print(f"Running simulation for {scenario_type.value} scenario...")
            
            # Run simulation
            sim_results = self.simulate_adoption_scenario(scenario_type, policy_effects)
            
            # Calculate statistics
            stats_dict = {}
            for metric, data in sim_results.items():
                if metric != 'years':
                    stats_dict[metric] = {
                        'mean': np.mean(data, axis=0),
                        'median': np.median(data, axis=0),
                        'p5': np.percentile(data, 5, axis=0),
                        'p25': np.percentile(data, 25, axis=0),
                        'p75': np.percentile(data, 75, axis=0),
                        'p95': np.percentile(data, 95, axis=0),
                        'std': np.std(data, axis=0)
                    }
            
            results[scenario_type.value] = {
                'raw_data': sim_results,
                'statistics': stats_dict
            }
        
        self.results = results
        return results
    
    def calculate_economic_impact(self, scenario_results: Dict) -> Dict[str, float]:
        """
        Calculate economic impact metrics for a scenario.
        
        Args:
            scenario_results: Results from a simulation scenario
            
        Returns:
            Dictionary with economic impact metrics
        """
        final_year_idx = -1
        
        # Market size impact
        market_size_mean = scenario_results['statistics']['market_size']['mean'][final_year_idx]
        market_size_p25 = scenario_results['statistics']['market_size']['p25'][final_year_idx]
        market_size_p75 = scenario_results['statistics']['market_size']['p75'][final_year_idx]
        
        # Adoption rates
        overall_adoption = scenario_results['statistics']['overall_adoption']['mean'][final_year_idx]
        sme_adoption = scenario_results['statistics']['sme_adoption']['mean'][final_year_idx]
        large_adoption = scenario_results['statistics']['large_adoption']['mean'][final_year_idx]
        
        # Economic multipliers (based on research)
        gdp_multiplier = 3.5  # Each USD of AI investment creates $3.5 GDP
        jobs_per_billion = 8500  # Jobs per billion USD AI investment
        productivity_multiplier = 0.22  # Max 22% productivity gain
        
        # Calculate impacts
        gdp_impact = market_size_mean * gdp_multiplier
        jobs_impact = market_size_mean * jobs_per_billion
        productivity_impact = overall_adoption * productivity_multiplier
        
        return {
            'market_size_billion_usd': market_size_mean,
            'market_size_range': (market_size_p25, market_size_p75),
            'overall_adoption_rate': overall_adoption,
            'sme_adoption_rate': sme_adoption,
            'large_adoption_rate': large_adoption,
            'gdp_impact_billion_usd': gdp_impact,
            'jobs_created': int(jobs_impact),
            'productivity_gain_percent': productivity_impact * 100
        }
    
    def generate_policy_recommendations(self) -> List[Dict[str, str]]:
        """
        Generate policy recommendations based on simulation results.
        
        Returns:
            List of policy recommendations
        """
        if not self.results:
            raise ValueError("Must run analysis before generating recommendations")
        
        baseline = self.results['baseline']
        policy = self.results['policy_intervention']
        
        # Compare scenarios
        baseline_impact = self.calculate_economic_impact(baseline)
        policy_impact = self.calculate_economic_impact(policy)
        
        recommendations = []
        
        # SME adoption gap
        if policy_impact['sme_adoption_rate'] > baseline_impact['sme_adoption_rate'] * 1.1:
            recommendations.append({
                'priority': 'High',
                'area': 'SME Support',
                'recommendation': 'Implement comprehensive SME AI support program',
                'impact': f"Could increase SME adoption from {baseline_impact['sme_adoption_rate']:.1%} to {policy_impact['sme_adoption_rate']:.1%}",
                'economic_benefit': f"Additional ${policy_impact['gdp_impact_billion_usd'] - baseline_impact['gdp_impact_billion_usd']:.1f}B GDP impact"
            })
        
        # Market size growth
        market_growth = (policy_impact['market_size_billion_usd'] / baseline_impact['market_size_billion_usd'] - 1) * 100
        if market_growth > 5:
            recommendations.append({
                'priority': 'High',
                'area': 'Market Development',
                'recommendation': 'Accelerate market development through policy intervention',
                'impact': f"Could increase market size by {market_growth:.1f}%",
                'economic_benefit': f"Market size could reach ${policy_impact['market_size_billion_usd']:.1f}B vs ${baseline_impact['market_size_billion_usd']:.1f}B baseline"
            })
        
        # Job creation
        job_difference = policy_impact['jobs_created'] - baseline_impact['jobs_created']
        if job_difference > 10000:
            recommendations.append({
                'priority': 'Medium',
                'area': 'Employment',
                'recommendation': 'Focus on AI job creation and workforce development',
                'impact': f"Could create additional {job_difference:,} jobs",
                'economic_benefit': f"Total AI jobs: {policy_impact['jobs_created']:,}"
            })
        
        return recommendations
    
    def export_results(self, filename: str = 'ai_simulation_results.json'):
        """
        Export simulation results to JSON file.
        
        Args:
            filename: Output filename
        """
        if not self.results:
            raise ValueError("No results to export. Run analysis first.")
        
        # Convert numpy arrays to lists for JSON serialization
        export_data = {}
        for scenario, data in self.results.items():
            export_data[scenario] = {
                'statistics': {},
                'economic_impact': self.calculate_economic_impact(data)
            }
            
            for metric, stats in data['statistics'].items():
                export_data[scenario]['statistics'][metric] = {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in stats.items()
                }
        
        # Add policy recommendations
        export_data['policy_recommendations'] = self.generate_policy_recommendations()
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results exported to {filename}")


if __name__ == '__main__':
    # Demonstration of the simulation engine
    print("AI Investment Simulation Engine Demo")
    print("=" * 50)
    
    # Initialize simulator
    params = SimulationParameters(num_simulations=500)  # Reduced for demo
    simulator = AIAdoptionSimulator(params)
    
    # Run comprehensive analysis
    print("\nRunning comprehensive scenario analysis...")
    results = simulator.run_comprehensive_analysis()
    
    # Display results summary
    print("\nScenario Analysis Results (2030 projections):")
    print("-" * 60)
    
    for scenario_name, scenario_data in results.items():
        impact = simulator.calculate_economic_impact(scenario_data)
        print(f"\n{scenario_name.upper()}:")
        print(f"  Market Size: ${impact['market_size_billion_usd']:.1f}B")
        print(f"  Overall Adoption: {impact['overall_adoption_rate']:.1%}")
        print(f"  SME Adoption: {impact['sme_adoption_rate']:.1%}")
        print(f"  Large Enterprise Adoption: {impact['large_adoption_rate']:.1%}")
        print(f"  GDP Impact: ${impact['gdp_impact_billion_usd']:.1f}B")
        print(f"  Jobs Created: {impact['jobs_created']:,}")
        print(f"  Productivity Gain: {impact['productivity_gain_percent']:.1f}%")
    
    # Generate policy recommendations
    print("\nPolicy Recommendations:")
    print("-" * 40)
    
    recommendations = simulator.generate_policy_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['recommendation']} ({rec['priority']} Priority)")
        print(f"   Area: {rec['area']}")
        print(f"   Impact: {rec['impact']}")
        print(f"   Benefit: {rec['economic_benefit']}")
    
    # Export results
    print("\nExporting detailed results...")
    simulator.export_results('ai_simulation_results.json')
    
    print("\n" + "=" * 50)
    print("Simulation Engine Demo Complete!")
