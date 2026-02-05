import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class AdvancedFinancialAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.forecast_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
        # Industry-specific risk factors
        self.risk_weights = {
            'manufacturing': {'inventory_risk': 0.3, 'supply_chain_risk': 0.4, 'market_risk': 0.3},
            'retail': {'inventory_risk': 0.4, 'seasonal_risk': 0.3, 'competition_risk': 0.3},
            'services': {'client_concentration_risk': 0.4, 'talent_risk': 0.3, 'market_risk': 0.3},
            'agriculture': {'weather_risk': 0.4, 'commodity_risk': 0.3, 'seasonal_risk': 0.3},
            'logistics': {'fuel_risk': 0.3, 'regulatory_risk': 0.3, 'competition_risk': 0.4},
            'ecommerce': {'technology_risk': 0.3, 'competition_risk': 0.4, 'regulatory_risk': 0.3}
        }
    
    def calculate_working_capital_metrics(self, financial_data):
        """Calculate working capital optimization metrics"""
        metrics = {}
        
        # Days Sales Outstanding (DSO)
        if 'accounts_receivable' in financial_data and 'revenue' in financial_data:
            metrics['dso'] = (financial_data['accounts_receivable'] / financial_data['revenue']) * 365
        
        # Days Inventory Outstanding (DIO)
        if 'inventory' in financial_data and 'cost_of_goods_sold' in financial_data:
            metrics['dio'] = (financial_data['inventory'] / financial_data['cost_of_goods_sold']) * 365
        
        # Days Payable Outstanding (DPO)
        if 'accounts_payable' in financial_data and 'cost_of_goods_sold' in financial_data:
            metrics['dpo'] = (financial_data['accounts_payable'] / financial_data['cost_of_goods_sold']) * 365
        
        # Cash Conversion Cycle
        if all(k in metrics for k in ['dso', 'dio', 'dpo']):
            metrics['cash_conversion_cycle'] = metrics['dso'] + metrics['dio'] - metrics['dpo']
        
        return metrics
    
    def assess_financial_risks(self, financial_data, industry):
        """Comprehensive risk assessment"""
        risks = {}
        risk_score = 0
        
        # Liquidity Risk
        current_ratio = financial_data.get('current_assets', 0) / max(financial_data.get('current_liabilities', 1), 1)
        if current_ratio < 1.0:
            risks['liquidity_risk'] = 'High'
            risk_score += 30
        elif current_ratio < 1.5:
            risks['liquidity_risk'] = 'Medium'
            risk_score += 15
        else:
            risks['liquidity_risk'] = 'Low'
            risk_score += 5
        
        # Credit Risk
        debt_to_equity = financial_data.get('total_debt', 0) / max(financial_data.get('total_equity', 1), 1)
        if debt_to_equity > 2.0:
            risks['credit_risk'] = 'High'
            risk_score += 25
        elif debt_to_equity > 1.0:
            risks['credit_risk'] = 'Medium'
            risk_score += 12
        else:
            risks['credit_risk'] = 'Low'
            risk_score += 3
        
        # Operational Risk
        profit_margin = financial_data.get('net_income', 0) / max(financial_data.get('revenue', 1), 1)
        if profit_margin < 0:
            risks['operational_risk'] = 'High'
            risk_score += 20
        elif profit_margin < 0.05:
            risks['operational_risk'] = 'Medium'
            risk_score += 10
        else:
            risks['operational_risk'] = 'Low'
            risk_score += 2
        
        # Industry-specific risks
        industry_risks = self.risk_weights.get(industry, {})
        for risk_type, weight in industry_risks.items():
            # Simplified industry risk calculation
            industry_risk_score = np.random.uniform(0.1, 0.8) * weight * 20
            risk_score += industry_risk_score
            risks[risk_type] = 'Medium' if industry_risk_score > 10 else 'Low'
        
        risks['overall_risk_score'] = min(risk_score, 100)
        risks['risk_grade'] = self._get_risk_grade(risk_score)
        
        return risks
    
    def _get_risk_grade(self, score):
        """Convert risk score to grade"""
        if score <= 20:
            return 'A'
        elif score <= 40:
            return 'B'
        elif score <= 60:
            return 'C'
        else:
            return 'D'
    
    def forecast_financial_metrics(self, historical_data, periods=12):
        """Forecast financial metrics using ML"""
        if len(historical_data) < 6:
            return self._generate_simple_forecast(historical_data, periods)
        
        # Prepare data for forecasting
        df = pd.DataFrame(historical_data)
        df['period'] = range(len(df))
        
        forecasts = {}
        
        for metric in ['revenue', 'net_income', 'cash_flow']:
            if metric in df.columns:
                X = df[['period']].values
                y = df[metric].values
                
                # Train model
                self.forecast_model.fit(X, y)
                
                # Generate forecasts
                future_periods = np.array([[len(df) + i] for i in range(1, periods + 1)])
                predictions = self.forecast_model.predict(future_periods)
                
                forecasts[metric] = {
                    'predictions': predictions.tolist(),
                    'confidence': self._calculate_confidence(X, y, future_periods)
                }
        
        return forecasts
    
    def _generate_simple_forecast(self, historical_data, periods):
        """Simple trend-based forecast for limited data"""
        forecasts = {}
        
        for metric in ['revenue', 'net_income', 'cash_flow']:
            if len(historical_data) > 0 and metric in historical_data[-1]:
                last_value = historical_data[-1][metric]
                growth_rate = 0.05  # Assume 5% growth
                
                predictions = []
                for i in range(1, periods + 1):
                    predicted_value = last_value * (1 + growth_rate) ** i
                    predictions.append(predicted_value)
                
                forecasts[metric] = {
                    'predictions': predictions,
                    'confidence': [0.7] * periods  # Lower confidence for simple forecast
                }
        
        return forecasts
    
    def _calculate_confidence(self, X, y, future_X):
        """Calculate prediction confidence intervals"""
        # Simplified confidence calculation
        mae = mean_absolute_error(y, self.forecast_model.predict(X))
        confidence = np.maximum(0.5, 1 - (mae / np.mean(y)))
        return [confidence] * len(future_X)
    
    def detect_financial_anomalies(self, financial_data):
        """Detect unusual patterns in financial data"""
        # Convert financial data to feature matrix
        features = []
        feature_names = []
        
        for key, value in financial_data.items():
            if isinstance(value, (int, float)) and not np.isnan(value):
                features.append(value)
                feature_names.append(key)
        
        if len(features) < 3:
            return {'anomalies': [], 'anomaly_score': 0}
        
        # Reshape for anomaly detection
        X = np.array(features).reshape(1, -1)
        
        # Fit and predict anomalies
        self.anomaly_detector.fit(X)
        anomaly_score = self.anomaly_detector.decision_function(X)[0]
        is_anomaly = self.anomaly_detector.predict(X)[0] == -1
        
        anomalies = []
        if is_anomaly:
            # Identify which features contribute to anomaly
            for i, (name, value) in enumerate(zip(feature_names, features)):
                if abs(value) > np.percentile(features, 95):
                    anomalies.append({
                        'metric': name,
                        'value': value,
                        'severity': 'High' if abs(anomaly_score) > 0.5 else 'Medium'
                    })
        
        return {
            'anomalies': anomalies,
            'anomaly_score': float(anomaly_score),
            'is_anomalous': bool(is_anomaly)
        }
    
    def generate_cost_optimization_recommendations(self, financial_data, industry):
        """Generate cost optimization strategies"""
        recommendations = []
        
        # Revenue per employee analysis
        if 'revenue' in financial_data and 'employee_count' in financial_data:
            revenue_per_employee = financial_data['revenue'] / max(financial_data['employee_count'], 1)
            industry_benchmark = self._get_industry_benchmark(industry, 'revenue_per_employee')
            
            if revenue_per_employee < industry_benchmark * 0.8:
                recommendations.append({
                    'category': 'Productivity',
                    'recommendation': 'Consider automation or training programs to improve revenue per employee',
                    'potential_savings': financial_data['revenue'] * 0.1,
                    'implementation_time': '3-6 months'
                })
        
        # Operating expense ratio analysis
        if 'operating_expenses' in financial_data and 'revenue' in financial_data:
            opex_ratio = financial_data['operating_expenses'] / financial_data['revenue']
            if opex_ratio > 0.8:
                recommendations.append({
                    'category': 'Cost Control',
                    'recommendation': 'Review and optimize operating expenses - consider renegotiating contracts',
                    'potential_savings': financial_data['operating_expenses'] * 0.15,
                    'implementation_time': '1-3 months'
                })
        
        # Inventory optimization
        if 'inventory' in financial_data and 'cost_of_goods_sold' in financial_data:
            inventory_turnover = financial_data['cost_of_goods_sold'] / financial_data['inventory']
            if inventory_turnover < 4:  # Less than quarterly turnover
                recommendations.append({
                    'category': 'Inventory Management',
                    'recommendation': 'Implement just-in-time inventory management to reduce carrying costs',
                    'potential_savings': financial_data['inventory'] * 0.2,
                    'implementation_time': '2-4 months'
                })
        
        return recommendations
    
    def _get_industry_benchmark(self, industry, metric):
        """Get industry benchmark values"""
        benchmarks = {
            'manufacturing': {'revenue_per_employee': 200000},
            'retail': {'revenue_per_employee': 150000},
            'services': {'revenue_per_employee': 180000},
            'agriculture': {'revenue_per_employee': 120000},
            'logistics': {'revenue_per_employee': 160000},
            'ecommerce': {'revenue_per_employee': 250000}
        }
        
        return benchmarks.get(industry, {}).get(metric, 150000)
    
    def calculate_financial_health_score(self, financial_data, ratios, risks, industry):
        """Calculate comprehensive financial health score"""
        score = 100
        
        # Profitability (25%)
        profit_margin = ratios.get('profit_margin', 0)
        if profit_margin < 0:
            score -= 25
        elif profit_margin < 0.05:
            score -= 15
        elif profit_margin < 0.1:
            score -= 5
        
        # Liquidity (25%)
        current_ratio = ratios.get('current_ratio', 0)
        if current_ratio < 1.0:
            score -= 25
        elif current_ratio < 1.2:
            score -= 15
        elif current_ratio < 1.5:
            score -= 5
        
        # Leverage (25%)
        debt_to_equity = ratios.get('debt_to_equity', 0)
        if debt_to_equity > 2.0:
            score -= 25
        elif debt_to_equity > 1.5:
            score -= 15
        elif debt_to_equity > 1.0:
            score -= 5
        
        # Risk Assessment (25%)
        risk_score = risks.get('overall_risk_score', 0)
        score -= (risk_score * 0.25)
        
        return max(0, min(100, score))
    
    def generate_investor_report(self, financial_data, ratios, forecasts, industry):
        """Generate investor-ready financial report"""
        report = {
            'executive_summary': {
                'business_type': industry,
                'financial_health_score': self.calculate_financial_health_score(
                    financial_data, ratios, {}, industry
                ),
                'key_strengths': [],
                'key_concerns': []
            },
            'financial_metrics': ratios,
            'forecasts': forecasts,
            'investment_highlights': [],
            'risk_factors': [],
            'growth_opportunities': []
        }
        
        # Identify strengths and concerns
        if ratios.get('profit_margin', 0) > 0.1:
            report['executive_summary']['key_strengths'].append('Strong profit margins')
        if ratios.get('current_ratio', 0) > 1.5:
            report['executive_summary']['key_strengths'].append('Excellent liquidity position')
        
        if ratios.get('debt_to_equity', 0) > 1.5:
            report['executive_summary']['key_concerns'].append('High debt burden')
        if ratios.get('profit_margin', 0) < 0.05:
            report['executive_summary']['key_concerns'].append('Low profitability')
        
        return report