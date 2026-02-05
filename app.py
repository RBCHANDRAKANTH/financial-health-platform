from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import openai
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.graph_objects as go
import plotly.utils
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import PyPDF2
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize encryption
encryption_key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(encryption_key)

# OpenAI API setup
openai.api_key = os.environ.get('OPENAI_API_KEY')

class FinancialAnalyzer:
    def __init__(self):
        self.industry_benchmarks = {
            'manufacturing': {'current_ratio': 1.5, 'debt_to_equity': 0.6, 'profit_margin': 0.08},
            'retail': {'current_ratio': 1.2, 'debt_to_equity': 0.8, 'profit_margin': 0.05},
            'services': {'current_ratio': 1.3, 'debt_to_equity': 0.5, 'profit_margin': 0.12},
            'agriculture': {'current_ratio': 1.4, 'debt_to_equity': 0.7, 'profit_margin': 0.06},
            'logistics': {'current_ratio': 1.1, 'debt_to_equity': 0.9, 'profit_margin': 0.04},
            'ecommerce': {'current_ratio': 1.6, 'debt_to_equity': 0.4, 'profit_margin': 0.10}
        }
    
    def calculate_financial_ratios(self, data):
        """Calculate key financial ratios"""
        ratios = {}
        
        # Liquidity ratios
        if 'current_assets' in data and 'current_liabilities' in data:
            ratios['current_ratio'] = data['current_assets'] / max(data['current_liabilities'], 1)
        
        # Profitability ratios
        if 'net_income' in data and 'revenue' in data:
            ratios['profit_margin'] = data['net_income'] / max(data['revenue'], 1)
        
        # Leverage ratios
        if 'total_debt' in data and 'total_equity' in data:
            ratios['debt_to_equity'] = data['total_debt'] / max(data['total_equity'], 1)
        
        # Efficiency ratios
        if 'revenue' in data and 'total_assets' in data:
            ratios['asset_turnover'] = data['revenue'] / max(data['total_assets'], 1)
        
        return ratios
    
    def assess_creditworthiness(self, financial_data, ratios):
        """AI-powered creditworthiness assessment"""
        score = 100
        risk_factors = []
        
        # Current ratio assessment
        if ratios.get('current_ratio', 0) < 1.0:
            score -= 20
            risk_factors.append("Low liquidity - current ratio below 1.0")
        elif ratios.get('current_ratio', 0) < 1.2:
            score -= 10
            risk_factors.append("Moderate liquidity concern")
        
        # Debt assessment
        if ratios.get('debt_to_equity', 0) > 1.0:
            score -= 15
            risk_factors.append("High debt burden")
        
        # Profitability assessment
        if ratios.get('profit_margin', 0) < 0:
            score -= 25
            risk_factors.append("Negative profit margins")
        elif ratios.get('profit_margin', 0) < 0.05:
            score -= 10
            risk_factors.append("Low profit margins")
        
        # Cash flow assessment
        if financial_data.get('operating_cash_flow', 0) < 0:
            score -= 20
            risk_factors.append("Negative operating cash flow")
        
        credit_grade = 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'
        
        return {
            'score': max(score, 0),
            'grade': credit_grade,
            'risk_factors': risk_factors
        }
    
    def generate_recommendations(self, financial_data, ratios, industry):
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Industry benchmarking
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['services'])
        
        if ratios.get('current_ratio', 0) < benchmarks['current_ratio']:
            recommendations.append({
                'category': 'Liquidity',
                'priority': 'High',
                'recommendation': 'Improve working capital management by optimizing inventory levels and accelerating receivables collection'
            })
        
        if ratios.get('profit_margin', 0) < benchmarks['profit_margin']:
            recommendations.append({
                'category': 'Profitability',
                'priority': 'High',
                'recommendation': 'Focus on cost optimization and pricing strategy review to improve profit margins'
            })
        
        if ratios.get('debt_to_equity', 0) > benchmarks['debt_to_equity']:
            recommendations.append({
                'category': 'Leverage',
                'priority': 'Medium',
                'recommendation': 'Consider debt restructuring or equity financing to improve capital structure'
            })
        
        return recommendations

analyzer = FinancialAnalyzer()

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'financial_health'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        cursor_factory=RealDictCursor
    )

def encrypt_data(data):
    """Encrypt sensitive financial data"""
    return cipher_suite.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data):
    """Decrypt sensitive financial data"""
    return json.loads(cipher_suite.decrypt(encrypted_data).decode())

def parse_financial_document(file):
    """Parse uploaded financial documents"""
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    
    if file_ext == 'csv':
        return pd.read_csv(file)
    elif file_ext in ['xlsx', 'xls']:
        return pd.read_excel(file)
    elif file_ext == 'pdf':
        # Basic PDF text extraction
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return {'pdf_text': text}
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_financial_data():
    """Upload and process financial documents"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        data = parse_financial_document(file)
        business_type = request.form.get('business_type', 'services')
        
        # Extract financial metrics from uploaded data
        financial_data = extract_financial_metrics(data, business_type)
        
        # Calculate ratios
        ratios = analyzer.calculate_financial_ratios(financial_data)
        
        # Assess creditworthiness
        credit_assessment = analyzer.assess_creditworthiness(financial_data, ratios)
        
        # Generate recommendations
        recommendations = analyzer.generate_recommendations(financial_data, ratios, business_type)
        
        # Store encrypted data in database
        conn = get_db_connection()
        cur = conn.cursor()
        
        encrypted_data = encrypt_data({
            'financial_data': financial_data,
            'ratios': ratios,
            'assessment': credit_assessment,
            'recommendations': recommendations
        })
        
        cur.execute("""
            INSERT INTO assessments (business_type, encrypted_data, created_at)
            VALUES (%s, %s, %s) RETURNING id
        """, (business_type, encrypted_data, datetime.now()))
        
        assessment_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'assessment_id': assessment_id,
            'ratios': ratios,
            'credit_assessment': credit_assessment,
            'recommendations': recommendations,
            'visualizations': generate_visualizations(financial_data, ratios)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_financial_metrics(data, business_type):
    """Extract financial metrics from parsed data"""
    if isinstance(data, pd.DataFrame):
        # Assume standard financial statement format
        metrics = {}
        
        # Try to extract common financial metrics
        for col in data.columns:
            col_lower = col.lower()
            if 'revenue' in col_lower or 'sales' in col_lower:
                metrics['revenue'] = data[col].sum()
            elif 'net income' in col_lower or 'profit' in col_lower:
                metrics['net_income'] = data[col].sum()
            elif 'current assets' in col_lower:
                metrics['current_assets'] = data[col].sum()
            elif 'current liabilities' in col_lower:
                metrics['current_liabilities'] = data[col].sum()
            elif 'total debt' in col_lower:
                metrics['total_debt'] = data[col].sum()
            elif 'equity' in col_lower:
                metrics['total_equity'] = data[col].sum()
        
        return metrics
    
    # Default sample data for demonstration
    return {
        'revenue': 1000000,
        'net_income': 80000,
        'current_assets': 300000,
        'current_liabilities': 200000,
        'total_debt': 400000,
        'total_equity': 500000,
        'operating_cash_flow': 120000
    }

def generate_visualizations(financial_data, ratios):
    """Generate financial visualizations"""
    # Financial health dashboard
    fig = go.Figure()
    
    # Add ratio visualization
    categories = list(ratios.keys())
    values = list(ratios.values())
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        name='Financial Ratios',
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title='Financial Ratios Overview',
        xaxis_title='Ratios',
        yaxis_title='Values'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/api/assessment/<int:assessment_id>')
def get_assessment(assessment_id):
    """Retrieve stored assessment"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM assessments WHERE id = %s", (assessment_id,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({'error': 'Assessment not found'}), 404
        
        decrypted_data = decrypt_data(result['encrypted_data'])
        
        cur.close()
        conn.close()
        
        return jsonify(decrypted_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-insights', methods=['POST'])
def get_ai_insights():
    """Get AI-powered financial insights"""
    try:
        data = request.json
        financial_data = data.get('financial_data', {})
        business_type = data.get('business_type', 'services')
        
        # Generate AI insights using OpenAI
        prompt = f"""
        Analyze the following financial data for a {business_type} business:
        {json.dumps(financial_data, indent=2)}
        
        Provide:
        1. Key financial strengths
        2. Areas of concern
        3. Specific actionable recommendations
        4. Industry-specific insights
        
        Keep the response concise and actionable.
        """
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        return jsonify({
            'ai_insights': response.choices[0].text.strip()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)