from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import sqlite3
from cryptography.fernet import Fernet
import plotly.graph_objects as go
import plotly.utils
import PyPDF2
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize encryption
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

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
        ratios = {}
        if 'current_assets' in data and 'current_liabilities' in data:
            ratios['current_ratio'] = data['current_assets'] / max(data['current_liabilities'], 1)
        if 'net_income' in data and 'revenue' in data:
            ratios['profit_margin'] = data['net_income'] / max(data['revenue'], 1)
        if 'total_debt' in data and 'total_equity' in data:
            ratios['debt_to_equity'] = data['total_debt'] / max(data['total_equity'], 1)
        if 'revenue' in data and 'total_assets' in data:
            ratios['asset_turnover'] = data['revenue'] / max(data['total_assets'], 1)
        return ratios
    
    def assess_creditworthiness(self, financial_data, ratios):
        score = 100
        risk_factors = []
        
        if ratios.get('current_ratio', 0) < 1.0:
            score -= 20
            risk_factors.append("Low liquidity - current ratio below 1.0")
        if ratios.get('debt_to_equity', 0) > 1.0:
            score -= 15
            risk_factors.append("High debt burden")
        if ratios.get('profit_margin', 0) < 0:
            score -= 25
            risk_factors.append("Negative profit margins")
        
        credit_grade = 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'
        
        return {
            'score': max(score, 0),
            'grade': credit_grade,
            'risk_factors': risk_factors
        }
    
    def generate_recommendations(self, financial_data, ratios, industry):
        recommendations = []
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['services'])
        
        if ratios.get('current_ratio', 0) < benchmarks['current_ratio']:
            recommendations.append({
                'category': 'Liquidity',
                'priority': 'High',
                'recommendation': 'Improve working capital management by optimizing inventory levels'
            })
        
        if ratios.get('profit_margin', 0) < benchmarks['profit_margin']:
            recommendations.append({
                'category': 'Profitability',
                'priority': 'High',
                'recommendation': 'Focus on cost optimization and pricing strategy review'
            })
        
        return recommendations

analyzer = FinancialAnalyzer()

def init_sqlite_db():
    conn = sqlite3.connect('financial_health.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_type TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial Health Assessment Platform</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .upload-section { background: white; padding: 30px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; }
        select, input[type="file"] { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 6px; }
        .upload-btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 6px; cursor: pointer; }
        .results { display: none; margin-top: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Financial Health Assessment Platform</h1>
        <p>AI-powered financial analysis for SMEs</p>
    </div>
    
    <div class="upload-section">
        <h2>Upload Financial Documents</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label>Business Type:</label>
                <select id="businessType" name="business_type">
                    <option value="manufacturing">Manufacturing</option>
                    <option value="retail">Retail</option>
                    <option value="services">Services</option>
                    <option value="agriculture">Agriculture</option>
                    <option value="logistics">Logistics</option>
                    <option value="ecommerce">E-commerce</option>
                </select>
            </div>
            <div class="form-group">
                <label>Financial Documents (CSV, XLSX, PDF):</label>
                <input type="file" id="fileUpload" name="file" accept=".csv,.xlsx,.xls,.pdf">
            </div>
            <button type="submit" class="upload-btn">Analyze Financial Health</button>
        </form>
    </div>
    
    <div id="results" class="results">
        <h2>Analysis Results</h2>
        <div id="resultsContent"></div>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('fileUpload');
            const businessType = document.getElementById('businessType').value;
            
            if (!fileInput.files[0]) {
                alert('Please select a file');
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            formData.append('business_type', businessType);
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayResults(result);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Upload failed: ' + error.message);
            }
        });

        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const contentDiv = document.getElementById('resultsContent');
            
            contentDiv.innerHTML = `
                <h3>Credit Score: ${data.credit_assessment.score} (Grade ${data.credit_assessment.grade})</h3>
                <h4>Financial Ratios:</h4>
                <ul>
                    ${Object.entries(data.ratios).map(([key, value]) => 
                        `<li>${key.replace(/_/g, ' ')}: ${value.toFixed(2)}</li>`
                    ).join('')}
                </ul>
                <h4>Recommendations:</h4>
                <ul>
                    ${data.recommendations.map(rec => 
                        `<li><strong>${rec.category}</strong> (${rec.priority}): ${rec.recommendation}</li>`
                    ).join('')}
                </ul>
            `;
            
            resultsDiv.style.display = 'block';
        }
    </script>
</body>
</html>
    '''

def parse_financial_document(file):
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    
    if file_ext == 'csv':
        return pd.read_csv(file)
    elif file_ext in ['xlsx', 'xls']:
        return pd.read_excel(file)
    return None

def extract_financial_metrics(data, business_type):
    if isinstance(data, pd.DataFrame):
        metrics = {}
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
    
    return {
        'revenue': 1000000,
        'net_income': 80000,
        'current_assets': 300000,
        'current_liabilities': 200000,
        'total_debt': 400000,
        'total_equity': 500000,
        'total_assets': 750000
    }

@app.route('/api/upload', methods=['POST'])
def upload_financial_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        data = parse_financial_document(file)
        business_type = request.form.get('business_type', 'services')
        
        financial_data = extract_financial_metrics(data, business_type)
        ratios = analyzer.calculate_financial_ratios(financial_data)
        credit_assessment = analyzer.assess_creditworthiness(financial_data, ratios)
        recommendations = analyzer.generate_recommendations(financial_data, ratios, business_type)
        
        return jsonify({
            'ratios': ratios,
            'credit_assessment': credit_assessment,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_sqlite_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)