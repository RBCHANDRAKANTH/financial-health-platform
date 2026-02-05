import requests
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os

class BankingIntegration:
    def __init__(self, encryption_key):
        self.cipher_suite = Fernet(encryption_key)
        self.supported_banks = ['hdfc', 'icici', 'sbi', 'axis']
        
    def encrypt_credentials(self, credentials):
        """Encrypt banking credentials"""
        return self.cipher_suite.encrypt(json.dumps(credentials).encode())
    
    def decrypt_credentials(self, encrypted_credentials):
        """Decrypt banking credentials"""
        return json.loads(self.cipher_suite.decrypt(encrypted_credentials).decode())
    
    def connect_hdfc_api(self, credentials):
        """Connect to HDFC Bank API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {credentials['access_token']}",
                'X-API-Key': credentials['api_key']
            }
            
            # Fetch account balance
            balance_response = requests.get(
                f"{credentials['base_url']}/accounts/{credentials['account_id']}/balance",
                headers=headers,
                timeout=30
            )
            
            # Fetch transaction history
            transactions_response = requests.get(
                f"{credentials['base_url']}/accounts/{credentials['account_id']}/transactions",
                headers=headers,
                params={'from_date': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')},
                timeout=30
            )
            
            return {
                'status': 'success',
                'balance': balance_response.json() if balance_response.status_code == 200 else None,
                'transactions': transactions_response.json() if transactions_response.status_code == 200 else None
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def connect_icici_api(self, credentials):
        """Connect to ICICI Bank API"""
        try:
            # Generate signature for ICICI API
            timestamp = str(int(datetime.now().timestamp()))
            message = f"{credentials['client_id']}{timestamp}"
            signature = hmac.new(
                credentials['client_secret'].encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-Client-Id': credentials['client_id'],
                'X-Timestamp': timestamp,
                'X-Signature': signature
            }
            
            # Fetch account information
            account_response = requests.get(
                f"{credentials['base_url']}/account-info",
                headers=headers,
                timeout=30
            )
            
            return {
                'status': 'success',
                'account_info': account_response.json() if account_response.status_code == 200 else None
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def analyze_banking_data(self, banking_data):
        """Analyze banking data for financial insights"""
        insights = {
            'cash_flow_analysis': {},
            'spending_patterns': {},
            'seasonal_trends': {},
            'risk_indicators': []
        }
        
        if 'transactions' in banking_data:
            transactions = banking_data['transactions']
            
            # Cash flow analysis
            monthly_inflows = {}
            monthly_outflows = {}
            
            for transaction in transactions:
                month = transaction.get('date', '')[:7]  # YYYY-MM format
                amount = float(transaction.get('amount', 0))
                
                if amount > 0:
                    monthly_inflows[month] = monthly_inflows.get(month, 0) + amount
                else:
                    monthly_outflows[month] = monthly_outflows.get(month, 0) + abs(amount)
            
            insights['cash_flow_analysis'] = {
                'monthly_inflows': monthly_inflows,
                'monthly_outflows': monthly_outflows,
                'net_cash_flow': {
                    month: monthly_inflows.get(month, 0) - monthly_outflows.get(month, 0)
                    for month in set(list(monthly_inflows.keys()) + list(monthly_outflows.keys()))
                }
            }
            
            # Identify risk indicators
            if any(flow < 0 for flow in insights['cash_flow_analysis']['net_cash_flow'].values()):
                insights['risk_indicators'].append('Negative cash flow detected in some months')
            
            # Large transaction analysis
            large_transactions = [t for t in transactions if abs(float(t.get('amount', 0))) > 100000]
            if len(large_transactions) > len(transactions) * 0.1:
                insights['risk_indicators'].append('High frequency of large transactions')
        
        return insights

class GSTIntegration:
    def __init__(self, encryption_key):
        self.cipher_suite = Fernet(encryption_key)
        self.gst_api_base = "https://api.gst.gov.in"
        
    def authenticate_gst_api(self, credentials):
        """Authenticate with GST API"""
        try:
            auth_payload = {
                'username': credentials['username'],
                'password': credentials['password'],
                'app_key': credentials['app_key']
            }
            
            response = requests.post(
                f"{self.gst_api_base}/taxpayerapi/v1.0/authenticate",
                json=auth_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('auth_token')
            else:
                return None
                
        except Exception as e:
            print(f"GST authentication error: {e}")
            return None
    
    def fetch_gst_returns(self, gstin, auth_token, return_period):
        """Fetch GST return data"""
        try:
            headers = {
                'Authorization': f"Bearer {auth_token}",
                'Content-Type': 'application/json',
                'gstin': gstin
            }
            
            # Fetch GSTR1 data
            gstr1_response = requests.get(
                f"{self.gst_api_base}/taxpayerapi/v1.0/returns/gstr1",
                headers=headers,
                params={'ret_period': return_period},
                timeout=30
            )
            
            # Fetch GSTR3B data
            gstr3b_response = requests.get(
                f"{self.gst_api_base}/taxpayerapi/v1.0/returns/gstr3b",
                headers=headers,
                params={'ret_period': return_period},
                timeout=30
            )
            
            return {
                'gstr1': gstr1_response.json() if gstr1_response.status_code == 200 else None,
                'gstr3b': gstr3b_response.json() if gstr3b_response.status_code == 200 else None
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_gst_compliance(self, gst_data):
        """Analyze GST compliance and identify issues"""
        compliance_analysis = {
            'compliance_score': 100,
            'issues': [],
            'recommendations': [],
            'tax_efficiency': {}
        }
        
        if 'gstr3b' in gst_data and gst_data['gstr3b']:
            gstr3b = gst_data['gstr3b']
            
            # Check for late filing
            if gst_data.get('filing_date') and gst_data.get('due_date'):
                if gst_data['filing_date'] > gst_data['due_date']:
                    compliance_analysis['compliance_score'] -= 20
                    compliance_analysis['issues'].append('Late filing detected')
            
            # Analyze tax liability vs input credit
            tax_liability = gstr3b.get('tax_liability', 0)
            input_credit = gstr3b.get('input_tax_credit', 0)
            
            if input_credit > tax_liability * 0.8:
                compliance_analysis['recommendations'].append(
                    'High input tax credit utilization - ensure proper documentation'
                )
            
            # Calculate effective tax rate
            turnover = gstr3b.get('turnover', 1)
            effective_tax_rate = (tax_liability / turnover) * 100
            
            compliance_analysis['tax_efficiency'] = {
                'effective_tax_rate': effective_tax_rate,
                'input_credit_ratio': (input_credit / tax_liability) * 100 if tax_liability > 0 else 0
            }
        
        return compliance_analysis
    
    def generate_tax_optimization_suggestions(self, gst_data, financial_data):
        """Generate tax optimization suggestions"""
        suggestions = []
        
        # Input tax credit optimization
        if 'input_tax_credit' in gst_data and 'tax_liability' in gst_data:
            itc_utilization = (gst_data['input_tax_credit'] / gst_data['tax_liability']) * 100
            
            if itc_utilization < 70:
                suggestions.append({
                    'category': 'Input Tax Credit',
                    'suggestion': 'Improve input tax credit utilization by ensuring all eligible purchases are claimed',
                    'potential_savings': gst_data['tax_liability'] * 0.1
                })
        
        # Composition scheme analysis
        if financial_data.get('revenue', 0) < 1500000:  # 15 lakh threshold
            current_tax = gst_data.get('tax_liability', 0)
            composition_tax = financial_data.get('revenue', 0) * 0.01  # 1% for services
            
            if composition_tax < current_tax:
                suggestions.append({
                    'category': 'Tax Structure',
                    'suggestion': 'Consider opting for composition scheme to reduce tax burden',
                    'potential_savings': current_tax - composition_tax
                })
        
        return suggestions

class PaymentGatewayIntegration:
    def __init__(self):
        self.supported_gateways = ['razorpay', 'payu']
    
    def connect_razorpay(self, credentials):
        """Connect to Razorpay API"""
        try:
            auth = (credentials['key_id'], credentials['key_secret'])
            
            # Fetch payment analytics
            response = requests.get(
                'https://api.razorpay.com/v1/payments',
                auth=auth,
                params={
                    'from': int((datetime.now() - timedelta(days=30)).timestamp()),
                    'to': int(datetime.now().timestamp())
                },
                timeout=30
            )
            
            return {
                'status': 'success',
                'payments': response.json() if response.status_code == 200 else None
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def analyze_payment_patterns(self, payment_data):
        """Analyze payment patterns for business insights"""
        analysis = {
            'payment_methods': {},
            'success_rates': {},
            'seasonal_patterns': {},
            'customer_behavior': {}
        }
        
        if 'payments' in payment_data:
            payments = payment_data['payments']
            
            # Payment method analysis
            for payment in payments:
                method = payment.get('method', 'unknown')
                analysis['payment_methods'][method] = analysis['payment_methods'].get(method, 0) + 1
            
            # Success rate analysis
            successful_payments = [p for p in payments if p.get('status') == 'captured']
            total_payments = len(payments)
            
            analysis['success_rates'] = {
                'overall_success_rate': (len(successful_payments) / total_payments) * 100 if total_payments > 0 else 0,
                'total_successful': len(successful_payments),
                'total_attempted': total_payments
            }
        
        return analysis

# Integration manager class
class FinancialIntegrationManager:
    def __init__(self, encryption_key):
        self.banking = BankingIntegration(encryption_key)
        self.gst = GSTIntegration(encryption_key)
        self.payments = PaymentGatewayIntegration()
    
    def sync_all_data(self, business_id, integrations_config):
        """Sync data from all configured integrations"""
        synced_data = {
            'banking_data': {},
            'gst_data': {},
            'payment_data': {},
            'sync_timestamp': datetime.now().isoformat()
        }
        
        # Sync banking data
        if 'banking' in integrations_config:
            for bank_config in integrations_config['banking']:
                bank_name = bank_config['bank_name']
                credentials = self.banking.decrypt_credentials(bank_config['encrypted_credentials'])
                
                if bank_name == 'hdfc':
                    result = self.banking.connect_hdfc_api(credentials)
                elif bank_name == 'icici':
                    result = self.banking.connect_icici_api(credentials)
                
                synced_data['banking_data'][bank_name] = result
        
        # Sync GST data
        if 'gst' in integrations_config:
            gst_config = integrations_config['gst']
            credentials = self.gst.cipher_suite.decrypt(gst_config['encrypted_credentials'])
            credentials = json.loads(credentials.decode())
            
            auth_token = self.gst.authenticate_gst_api(credentials)
            if auth_token:
                gst_returns = self.gst.fetch_gst_returns(
                    gst_config['gstin'],
                    auth_token,
                    gst_config.get('return_period', '032024')
                )
                synced_data['gst_data'] = gst_returns
        
        # Sync payment gateway data
        if 'payments' in integrations_config:
            for payment_config in integrations_config['payments']:
                gateway_name = payment_config['gateway_name']
                
                if gateway_name == 'razorpay':
                    result = self.payments.connect_razorpay(payment_config['credentials'])
                    synced_data['payment_data'][gateway_name] = result
        
        return synced_data
    
    def generate_integrated_insights(self, synced_data, financial_data):
        """Generate insights from integrated data sources"""
        insights = {
            'cash_flow_reconciliation': {},
            'revenue_verification': {},
            'compliance_status': {},
            'operational_efficiency': {}
        }
        
        # Cash flow reconciliation
        banking_cash_flow = {}
        if synced_data['banking_data']:
            for bank, data in synced_data['banking_data'].items():
                if data.get('status') == 'success':
                    banking_insights = self.banking.analyze_banking_data(data)
                    banking_cash_flow[bank] = banking_insights['cash_flow_analysis']
        
        insights['cash_flow_reconciliation'] = banking_cash_flow
        
        # GST compliance analysis
        if synced_data['gst_data']:
            gst_compliance = self.gst.analyze_gst_compliance(synced_data['gst_data'])
            insights['compliance_status'] = gst_compliance
        
        return insights