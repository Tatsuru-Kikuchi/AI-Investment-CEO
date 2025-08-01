#!/usr/bin/env python3
"""
Advanced Predictive Models for AI Investment Analysis

This module contains sophisticated machine learning models to predict
AI adoption patterns based on executive demographics and firm characteristics.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AIAdoptionPredictor:
    """
    Advanced machine learning model to predict AI adoption likelihood
    based on executive demographics and firm characteristics.
    """
    
    def __init__(self):
        self.models = {
            'adoption_classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'investment_regressor': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'roi_predictor': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        self.scalers = {
            'features': StandardScaler(),
            'investment': StandardScaler()
        }
        self.encoders = {
            'industry': LabelEncoder(),
            'region': LabelEncoder(),
            'roi': LabelEncoder()
        }
        self.is_trained = False
    
    def generate_synthetic_data(self, n_samples: int = 5000) -> pd.DataFrame:
        """
        Generate synthetic dataset based on research findings for model training.
        
        Args:
            n_samples: Number of synthetic samples to generate
            
        Returns:
            DataFrame with synthetic company data
        """
        np.random.seed(42)
        
        # Generate executive demographics
        ages = np.random.choice(['40-49', '50-59', '60-69'], n_samples, p=[0.35, 0.45, 0.20])
        genders = np.random.choice(['male', 'female'], n_samples, p=[0.75, 0.25])
        
        # Generate firm characteristics
        firm_sizes = np.random.choice(['SME', 'Large'], n_samples, p=[0.70, 0.30])
        industries = np.random.choice(
            ['Service', 'Manufacturing', 'Retail', 'Finance', 'Healthcare'], 
            n_samples, 
            p=[0.25, 0.20, 0.20, 0.20, 0.15]
        )
        regions = np.random.choice(
            ['Tokyo', 'Osaka', 'Nagoya', 'Other'], 
            n_samples, 
            p=[0.40, 0.20, 0.15, 0.25]
        )
        
        # Generate revenue (in billions yen)
        revenues = []
        for size in firm_sizes:
            if size == 'SME':
                revenues.append(np.random.lognormal(mean=0.5, sigma=1.0))  # 0.1-10B yen
            else:
                revenues.append(np.random.lognormal(mean=2.5, sigma=0.8))  # 10-1000B yen
        
        # Calculate AI adoption probability based on research findings
        adoption_probs = []
        for age, gender, size, industry in zip(ages, genders, firm_sizes, industries):
            base_prob = 0.16 if size == 'SME' else 0.42  # Base adoption rates
            
            # Age adjustment
            age_multiplier = {'40-49': 1.2, '50-59': 1.0, '60-69': 0.8}[age]
            
            # Gender adjustment
            gender_multiplier = 1.1 if gender == 'male' else 0.9
            
            # Industry adjustment
            industry_multiplier = {
                'Service': 1.3, 'Finance': 1.4, 'Manufacturing': 1.0, 
                'Healthcare': 0.9, 'Retail': 0.8
            }[industry]
            
            prob = base_prob * age_multiplier * gender_multiplier * industry_multiplier
            adoption_probs.append(min(prob, 0.95))  # Cap at 95%
        
        # Generate actual adoption based on probabilities
        adoptions = np.random.binomial(1, adoption_probs)
        
        # Generate investment amounts (in millions yen)
        investments = []
        for adoption, revenue, size in zip(adoptions, revenues, firm_sizes):
            if adoption:
                base_investment = revenue * 0.03  # 3% of revenue
                if size == 'Large':
                    base_investment *= 1.5  # Large companies invest more
                investments.append(max(base_investment * np.random.lognormal(0, 0.3), 1.0))
            else:
                investments.append(0.0)
        
        # Generate ROI categories
        roi_categories = []
        for adoption, investment, size in zip(adoptions, investments, firm_sizes):
            if not adoption:
                roi_categories.append('None')
            else:
                if size == 'Large':
                    roi_prob = [0.15, 0.45, 0.30, 0.10]  # Low, Medium, High, Exceptional
                else:
                    roi_prob = [0.25, 0.50, 0.20, 0.05]  # SMEs have lower ROI distribution
                roi_categories.append(np.random.choice(
                    ['Low', 'Medium', 'High', 'Exceptional'], p=roi_prob
                ))
        
        # Create DataFrame
        data = pd.DataFrame({
            'executive_age': ages,
            'executive_gender': genders,
            'firm_size': firm_sizes,
            'industry': industries,
            'region': regions,
            'annual_revenue_billion_yen': revenues,
            'ai_adoption': adoptions,
            'ai_investment_million_yen': investments,
            'roi_category': roi_categories
        })
        
        return data
    
    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Prepare features for machine learning models.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Tuple of (feature_matrix, target_dict)
        """
        # Encode categorical variables
        data_encoded = data.copy()
        
        # Age encoding
        age_map = {'40-49': 0, '50-59': 1, '60-69': 2}
        data_encoded['age_encoded'] = data_encoded['executive_age'].map(age_map)
        
        # Gender encoding
        data_encoded['gender_encoded'] = (data_encoded['executive_gender'] == 'male').astype(int)
        
        # Firm size encoding
        data_encoded['size_encoded'] = (data_encoded['firm_size'] == 'Large').astype(int)
        
        # Industry encoding
        if not hasattr(self.encoders['industry'], 'classes_'):
            data_encoded['industry_encoded'] = self.encoders['industry'].fit_transform(data_encoded['industry'])
        else:
            data_encoded['industry_encoded'] = self.encoders['industry'].transform(data_encoded['industry'])
        
        # Region encoding
        if not hasattr(self.encoders['region'], 'classes_'):
            data_encoded['region_encoded'] = self.encoders['region'].fit_transform(data_encoded['region'])
        else:
            data_encoded['region_encoded'] = self.encoders['region'].transform(data_encoded['region'])
        
        # Revenue log transformation
        data_encoded['log_revenue'] = np.log1p(data_encoded['annual_revenue_billion_yen'])
        
        # Feature matrix
        feature_columns = [
            'age_encoded', 'gender_encoded', 'size_encoded', 'industry_encoded', 
            'region_encoded', 'log_revenue'
        ]
        X = data_encoded[feature_columns].values
        
        # Scale features
        if not hasattr(self.scalers['features'], 'scale_'):
            X_scaled = self.scalers['features'].fit_transform(X)
        else:
            X_scaled = self.scalers['features'].transform(X)
        
        # Targets
        targets = {
            'adoption': data_encoded['ai_adoption'].values,
            'investment': data_encoded['ai_investment_million_yen'].values,
            'roi': data_encoded['roi_category'].values
        }
        
        return X_scaled, targets
    
    def train_models(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Train all machine learning models.
        
        Args:
            data: Training data DataFrame
            
        Returns:
            Dictionary of model performance scores
        """
        X, targets = self.prepare_features(data)
        
        # Split data for adoption model
        X_train, X_test, y_adoption_train, y_adoption_test = train_test_split(
            X, targets['adoption'], test_size=0.2, random_state=42, stratify=targets['adoption']
        )
        
        # Train adoption classifier
        self.models['adoption_classifier'].fit(X_train, y_adoption_train)
        adoption_score = self.models['adoption_classifier'].score(X_test, y_adoption_test)
        
        # Train investment regressor (only on adopted cases)
        adopted_mask = targets['adoption'] == 1
        X_adopted = X[adopted_mask]
        y_investment = targets['investment'][adopted_mask]
        
        investment_score = 0.0
        if len(X_adopted) > 10:  # Ensure enough samples
            X_inv_train, X_inv_test, y_inv_train, y_inv_test = train_test_split(
                X_adopted, y_investment, test_size=0.2, random_state=42
            )
            
            self.models['investment_regressor'].fit(X_inv_train, y_inv_train)
            y_inv_pred = self.models['investment_regressor'].predict(X_inv_test)
            investment_score = r2_score(y_inv_test, y_inv_pred)
        
        # Train ROI classifier (only on adopted cases with non-None ROI)
        roi_mask = (targets['adoption'] == 1) & (targets['roi'] != 'None')
        X_roi = X[roi_mask]
        y_roi = targets['roi'][roi_mask]
        
        roi_score = 0.0
        if len(X_roi) > 10:  # Ensure enough samples
            # Encode ROI categories
            if not hasattr(self.encoders['roi'], 'classes_'):
                y_roi_encoded = self.encoders['roi'].fit_transform(y_roi)
            else:
                y_roi_encoded = self.encoders['roi'].transform(y_roi)
            
            X_roi_train, X_roi_test, y_roi_train, y_roi_test = train_test_split(
                X_roi, y_roi_encoded, test_size=0.2, random_state=42, stratify=y_roi_encoded
            )
            
            self.models['roi_predictor'].fit(X_roi_train, y_roi_train)
            roi_score = self.models['roi_predictor'].score(X_roi_test, y_roi_test)
        
        self.is_trained = True
        
        return {
            'adoption_accuracy': adoption_score,
            'investment_r2': investment_score,
            'roi_accuracy': roi_score
        }
    
    def predict_adoption_probability(self, executive_age: str, executive_gender: str, 
                                   firm_size: str, industry: str, region: str, 
                                   annual_revenue: float) -> Dict[str, float]:
        """
        Predict AI adoption probability for a given company profile.
        
        Args:
            executive_age: Age group ('40-49', '50-59', '60-69')
            executive_gender: Gender ('male', 'female')
            firm_size: Company size ('SME', 'Large')
            industry: Industry sector
            region: Geographic region
            annual_revenue: Annual revenue in billion yen
            
        Returns:
            Dictionary with predictions
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        # Create input DataFrame
        input_data = pd.DataFrame({
            'executive_age': [executive_age],
            'executive_gender': [executive_gender],
            'firm_size': [firm_size],
            'industry': [industry],
            'region': [region],
            'annual_revenue_billion_yen': [annual_revenue],
            'ai_adoption': [0],  # Dummy value
            'ai_investment_million_yen': [0],  # Dummy value
            'roi_category': ['None']  # Dummy value
        })
        
        # Prepare features
        X, _ = self.prepare_features(input_data)
        
        # Predict adoption probability
        adoption_prob = self.models['adoption_classifier'].predict_proba(X)[0, 1]
        
        # Predict investment amount if adopted
        investment_pred = 0.0
        if adoption_prob > 0.1:  # Only predict if reasonable adoption probability
            investment_pred = max(0, self.models['investment_regressor'].predict(X)[0])
        
        # Predict ROI category if adopted
        roi_pred = 'None'
        roi_probs = {}
        if adoption_prob > 0.1 and hasattr(self.encoders['roi'], 'classes_'):
            roi_pred_encoded = self.models['roi_predictor'].predict(X)[0]
            roi_pred = self.encoders['roi'].inverse_transform([roi_pred_encoded])[0]
            
            roi_prob_array = self.models['roi_predictor'].predict_proba(X)[0]
            roi_classes = self.encoders['roi'].classes_
            roi_probs = {cls: prob for cls, prob in zip(roi_classes, roi_prob_array)}
        
        return {
            'adoption_probability': adoption_prob,
            'predicted_investment_million_yen': investment_pred,
            'predicted_roi_category': roi_pred,
            'roi_probabilities': roi_probs
        }
    
    def analyze_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze feature importance across all models.
        
        Returns:
            Dictionary of feature importance for each model
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before analyzing feature importance")
        
        feature_names = ['Age', 'Gender', 'Firm Size', 'Industry', 'Region', 'Revenue']
        
        importance_dict = {}
        
        # Adoption model feature importance
        adoption_importance = self.models['adoption_classifier'].feature_importances_
        importance_dict['adoption'] = {name: imp for name, imp in zip(feature_names, adoption_importance)}
        
        # Investment model feature importance
        investment_importance = self.models['investment_regressor'].feature_importances_
        importance_dict['investment'] = {name: imp for name, imp in zip(feature_names, investment_importance)}
        
        # ROI model feature importance
        roi_importance = self.models['roi_predictor'].feature_importances_
        importance_dict['roi'] = {name: imp for name, imp in zip(feature_names, roi_importance)}
        
        return importance_dict


class AIMarketSimulator:
    """
    Simulate AI market evolution under different scenarios.
    """
    
    def __init__(self):
        self.base_data = {
            'market_size_2024': 7.56,  # Billion USD
            'market_size_2030': 26.80,  # Billion USD
            'cagr': 0.233,
            'sme_adoption_rate': 0.16,
            'large_adoption_rate': 0.42
        }
    
    def simulate_market_scenarios(self, years: int = 6) -> Dict[str, List[float]]:
        """
        Simulate different market evolution scenarios.
        
        Args:
            years: Number of years to simulate
            
        Returns:
            Dictionary with scenario projections
        """
        scenarios = {
            'baseline': [],
            'accelerated': [],
            'conservative': [],
            'policy_boost': []
        }
        
        base_size = self.base_data['market_size_2024']
        base_cagr = self.base_data['cagr']
        
        for year in range(years + 1):
            # Baseline scenario (current trajectory)
            baseline_size = base_size * (1 + base_cagr) ** year
            scenarios['baseline'].append(baseline_size)
            
            # Accelerated scenario (higher adoption rates)
            accel_cagr = base_cagr * 1.15
            accel_size = base_size * (1 + accel_cagr) ** year
            scenarios['accelerated'].append(accel_size)
            
            # Conservative scenario (slower growth)
            cons_cagr = base_cagr * 0.85
            cons_size = base_size * (1 + cons_cagr) ** year
            scenarios['conservative'].append(cons_size)
            
            # Policy boost scenario (government intervention effects)
            policy_multiplier = 1 + (0.05 * year)  # Growing policy impact
            policy_size = baseline_size * policy_multiplier
            scenarios['policy_boost'].append(policy_size)
        
        return scenarios
    
    def calculate_economic_impact(self, market_size: float, adoption_rate: float) -> Dict[str, float]:
        """
        Calculate economic impact of AI adoption.
        
        Args:
            market_size: AI market size in billion USD
            adoption_rate: Overall adoption rate (0-1)
            
        Returns:
            Dictionary with economic impact metrics
        """
        # Productivity gains based on adoption
        productivity_gain = adoption_rate * 0.22  # 22% max productivity gain
        
        # GDP impact (AI market size translates to broader economic impact)
        gdp_multiplier = 3.5  # Each dollar of AI investment creates $3.5 GDP
        gdp_impact = market_size * gdp_multiplier
        
        # Job impact
        jobs_per_billion = 8500  # Jobs created per billion USD of AI investment
        jobs_created = market_size * jobs_per_billion
        
        # Export potential
        export_multiplier = 0.15  # 15% of AI capabilities become exports
        export_potential = market_size * export_multiplier
        
        return {
            'productivity_gain_percent': productivity_gain * 100,
            'gdp_impact_billion_usd': gdp_impact,
            'jobs_created': int(jobs_created),
            'export_potential_billion_usd': export_potential
        }


class PolicyImpactAnalyzer:
    """
    Analyze the impact of different policy interventions on AI adoption.
    """
    
    def __init__(self):
        self.policy_effects = {
            'sme_support': {'adoption_boost': 0.15, 'investment_boost': 0.25},
            'gender_diversity': {'female_boost': 0.08, 'overall_boost': 0.03},
            'age_inclusion': {'senior_boost': 0.06, 'overall_boost': 0.02},
            'industry_hubs': {'sector_boost': 0.12, 'spillover': 0.04}
        }
    
    def evaluate_policy_combination(self, policies: List[str], base_adoption: float = 0.29) -> Dict[str, float]:
        """
        Evaluate the combined impact of multiple policies.
        
        Args:
            policies: List of policy names to apply
            base_adoption: Current baseline adoption rate
            
        Returns:
            Dictionary with policy impact results
        """
        total_boost = 0.0
        policy_costs = {
            'sme_support': 200,  # Billion yen
            'gender_diversity': 100,
            'age_inclusion': 75,
            'industry_hubs': 100
        }
        
        total_cost = 0.0
        
        for policy in policies:
            if policy in self.policy_effects:
                # Apply diminishing returns for multiple policies
                policy_boost = self.policy_effects[policy]['adoption_boost'] * (1 - total_boost * 0.3)
                total_boost += policy_boost
                total_cost += policy_costs.get(policy, 0)
        
        # Calculate results
        new_adoption_rate = min(base_adoption + total_boost, 0.85)  # Cap at 85%
        adoption_increase = new_adoption_rate - base_adoption
        
        # Economic benefits
        market_size_2030 = 26.80  # Billion USD
        additional_market = market_size_2030 * (adoption_increase / base_adoption)
        
        # ROI calculation
        total_cost_usd = total_cost * 0.0067  # Convert yen to USD (approximate)
        roi = (additional_market / total_cost_usd) if total_cost_usd > 0 else 0
        
        return {
            'new_adoption_rate': new_adoption_rate,
            'adoption_increase': adoption_increase,
            'policy_cost_billion_yen': total_cost,
            'additional_market_billion_usd': additional_market,
            'policy_roi': roi,
            'payback_years': (total_cost_usd / (additional_market / 6)) if additional_market > 0 else float('inf')
        }


if __name__ == '__main__':
    # Demonstrate the predictive models
    print("AI Investment Predictive Analytics Demo")
    print("=" * 50)
    
    # Initialize predictor
    predictor = AIAdoptionPredictor()
    
    # Generate synthetic data
    print("\n1. Generating synthetic training data...")
    training_data = predictor.generate_synthetic_data(n_samples=5000)
    print(f"Generated {len(training_data)} samples")
    print(f"Adoption rate in synthetic data: {training_data['ai_adoption'].mean():.1%}")
    
    # Train models
    print("\n2. Training predictive models...")
    performance = predictor.train_models(training_data)
    print("Model Performance:")
    for model, score in performance.items():
        print(f"  {model}: {score:.3f}")
    
    # Make sample predictions
    print("\n3. Sample Predictions:")
    
    test_cases = [
        ("45-year-old male CEO, Large Finance company, Tokyo, ¥50B revenue", 
         "40-49", "male", "Large", "Finance", "Tokyo", 50.0),
        ("55-year-old female CEO, SME Service company, Osaka, ¥2B revenue", 
         "50-59", "female", "SME", "Service", "Osaka", 2.0),
        ("62-year-old male CEO, Large Manufacturing, Nagoya, ¥100B revenue", 
         "60-69", "male", "Large", "Manufacturing", "Nagoya", 100.0)
    ]
    
    for description, age, gender, size, industry, region, revenue in test_cases:
        print(f"\n{description}:")
        prediction = predictor.predict_adoption_probability(
            age, gender, size, industry, region, revenue
        )
        print(f"  Adoption Probability: {prediction['adoption_probability']:.1%}")
        print(f"  Predicted Investment: ¥{prediction['predicted_investment_million_yen']:.1f}M")
        print(f"  Expected ROI Category: {prediction['predicted_roi_category']}")
    
    # Feature importance analysis
    print("\n4. Feature Importance Analysis:")
    importance = predictor.analyze_feature_importance()
    for model_name, features in importance.items():
        print(f"\n{model_name.title()} Model:")
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        for feature, imp in sorted_features:
            print(f"  {feature}: {imp:.3f}")
    
    # Market simulation
    print("\n5. Market Scenario Simulation:")
    simulator = AIMarketSimulator()
    scenarios = simulator.simulate_market_scenarios(6)
    
    print("Market Size Projections (Billion USD):")
    for scenario, values in scenarios.items():
        print(f"  {scenario.title()}: 2024=${values[0]:.1f}B → 2030=${values[-1]:.1f}B")
    
    # Policy impact analysis
    print("\n6. Policy Impact Analysis:")
    policy_analyzer = PolicyImpactAnalyzer()
    
    policy_combinations = [
        ['sme_support'],
        ['gender_diversity', 'age_inclusion'],
        ['sme_support', 'industry_hubs'],
        ['sme_support', 'gender_diversity', 'age_inclusion', 'industry_hubs']
    ]
    
    for policies in policy_combinations:
        result = policy_analyzer.evaluate_policy_combination(policies)
        print(f"\nPolicies: {', '.join(policies)}")
        print(f"  New Adoption Rate: {result['new_adoption_rate']:.1%}")
        print(f"  Additional Market: ${result['additional_market_billion_usd']:.1f}B")
        print(f"  Policy ROI: {result['policy_roi']:.1f}x")
        print(f"  Payback Period: {result['payback_years']:.1f} years")
    
    print("\n" + "=" * 50)
    print("Predictive Analytics Demo Complete!")
