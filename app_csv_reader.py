from flask import Flask, request, jsonify
import csv
import io
import os

app = Flask(__name__)

BENCHMARKS = {
    'manufacturing': (1.5, 0.6, 8.0),
    'retail': (1.2, 0.8, 5.0),
    'services': (1.3, 0.5, 12.0),
    'agriculture': (1.4, 0.7, 6.0),
    'logistics': (1.1, 0.9, 4.0),
    'ecommerce': (1.6, 0.4, 10.0)
}

def parse_csv(file_content):
    """Parse CSV and extract financial data"""
    reader = csv.DictReader(io.StringIO(file_content))
    data = {'revenue': 0, 'net_income': 0, 'current_assets': 0, 'current_liabilities': 0, 'total_debt': 0, 'total_equity': 0}
    
    for row in reader:
        account = row.get('Account', '').lower()
        amount = float(row.get('Amount', 0))
        
        if 'revenue' in account or 'sales' in account:
            data['revenue'] += amount
        elif 'net income' in account and amount > 0:
            data['net_income'] = amount
        elif 'cash' in account or 'receivable' in account or 'inventory' in account:
            data['current_assets'] += amount
        elif 'payable' in account or 'short-term' in account or 'credit' in account:
            data['current_liabilities'] += amount
        elif 'loan' in account or 'debt' in account:
            data['total_debt'] += amount
        elif 'equity' in account:
            data['total_equity'] += amount
    
    return data

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>Financial Health Assessment</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial;background:#f5f7fa}
.container{max-width:900px;margin:0 auto;padding:20px}.header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:25px;border-radius:8px;margin-bottom:25px}
.form{background:#fff;padding:25px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.1);margin-bottom:25px}
input,select,button{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:5px;font-size:14px}
button{background:#667eea;color:#fff;cursor:pointer;font-weight:600}button:hover{background:#5a67d8}
.results{background:#fff;padding:25px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.1);display:none}
.score{text-align:center;margin:20px 0}.score-circle{width:120px;height:120px;border-radius:50%;margin:0 auto 15px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;color:#fff}
.grade-a{background:#48bb78}.grade-b{background:#ed8936}.grade-c{background:#f56565}.grade-d{background:#e53e3e}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0}
.metric{background:#f8fafc;padding:15px;border-radius:6px;border-left:4px solid #667eea}
.recommendations{margin-top:20px}.rec{background:#f0fff4;border:1px solid #9ae6b4;padding:12px;border-radius:5px;margin:8px 0}
</style></head><body><div class="container">
<div class="header"><h1>Financial Health Assessment Platform</h1><p>Upload CSV files for AI-powered financial analysis</p></div>
<div class="form"><h2>Upload Financial Data</h2>
<select id="businessType"><option value="manufacturing">Manufacturing</option><option value="retail">Retail</option><option value="services">Services</option><option value="agriculture">Agriculture</option><option value="logistics">Logistics</option><option value="ecommerce">E-commerce</option></select>
<input type="file" id="csvFile" accept=".csv" style="padding:8px">
<button onclick="analyze()">Analyze CSV File</button></div>
<div id="results" class="results"><h2>Financial Health Assessment Results</h2><div id="resultsContent"></div></div></div>
<script>
function analyze(){
const fileInput = document.getElementById('csvFile');
const businessType = document.getElementById('businessType').value;
if(!fileInput.files[0]){alert('Please select a CSV file');return;}
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('business_type', businessType);
fetch('/api/upload',{method:'POST',body:formData})
.then(r=>r.json()).then(result=>{
document.getElementById('resultsContent').innerHTML=`<div class="score"><div class="score-circle grade-${result.grade.toLowerCase()}">${result.credit_score}</div><h3>Credit Grade: ${result.grade}</h3></div>
<div class="metrics"><div class="metric"><h4>Current Ratio</h4><p style="font-size:20px;color:#667eea">${result.current_ratio}</p></div>
<div class="metric"><h4>Profit Margin</h4><p style="font-size:20px;color:#667eea">${result.profit_margin}%</p></div>
<div class="metric"><h4>Debt Ratio</h4><p style="font-size:20px;color:#667eea">${result.debt_ratio}</p></div>
<div class="metric"><h4>Risk Level</h4><p style="font-size:20px;color:#667eea">${result.risk_level}</p></div></div>
<div class="recommendations"><h3>AI Recommendations</h3>${result.recommendations.map(r=>'<div class="rec">'+r+'</div>').join('')}</div>`;
document.getElementById('results').style.display='block'})}</script></body></html>'''

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        business_type = request.form['business_type']
        
        # Read CSV content
        file_content = file.read().decode('utf-8')
        data = parse_csv(file_content)
        
        # Calculate ratios
        current_ratio = data['current_assets'] / max(data['current_liabilities'], 1)
        profit_margin = (data['net_income'] / max(data['revenue'], 1)) * 100
        debt_ratio = data['total_debt'] / max(data['total_equity'], 1)
        
        # Credit scoring
        score = 100
        if current_ratio < 1.0: score -= 30
        if profit_margin < 5: score -= 25
        if debt_ratio > 1.0: score -= 20
        if profit_margin < 0: score -= 15
        
        grade = 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'
        risk_level = 'Low' if score >= 70 else 'Medium' if score >= 50 else 'High'
        
        # Recommendations
        recommendations = []
        if current_ratio < 1.2:
            recommendations.append("Critical: Improve liquidity immediately - current ratio too low")
        if profit_margin < 5:
            recommendations.append("Urgent: Focus on cost reduction and pricing optimization")
        if debt_ratio > 1.5:
            recommendations.append("High Priority: Reduce debt burden through restructuring")
        if profit_margin < 0:
            recommendations.append("Emergency: Business is losing money - immediate action required")
        
        return jsonify({
            'credit_score': max(score, 0),
            'grade': grade,
            'current_ratio': round(current_ratio, 2),
            'profit_margin': round(profit_margin, 2),
            'debt_ratio': round(debt_ratio, 2),
            'risk_level': risk_level,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))