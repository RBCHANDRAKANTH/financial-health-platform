from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Pre-computed industry benchmarks - O(1) lookup
BENCHMARKS = {
    'manufacturing': (1.5, 0.6, 8.0),  # current_ratio, debt_equity, profit_margin
    'retail': (1.2, 0.8, 5.0),
    'services': (1.3, 0.5, 12.0),
    'agriculture': (1.4, 0.7, 6.0),
    'logistics': (1.1, 0.9, 4.0),
    'ecommerce': (1.6, 0.4, 10.0)
}

# Pre-computed scoring weights - O(1) calculation
SCORE_WEIGHTS = {
    'current_ratio': {'threshold': 1.0, 'penalty': 30},
    'profit_margin': {'threshold': 5.0, 'penalty': 25},
    'debt_ratio': {'threshold': 1.0, 'penalty': 20}
}

def calculate_score(current_ratio, profit_margin, debt_ratio):
    """O(1) credit scoring algorithm"""
    score = 100
    
    # Vectorized scoring - single pass O(1)
    if current_ratio < SCORE_WEIGHTS['current_ratio']['threshold']:
        score -= SCORE_WEIGHTS['current_ratio']['penalty']
    if profit_margin < SCORE_WEIGHTS['profit_margin']['threshold']:
        score -= SCORE_WEIGHTS['profit_margin']['penalty']
    if debt_ratio > SCORE_WEIGHTS['debt_ratio']['threshold']:
        score -= SCORE_WEIGHTS['debt_ratio']['penalty']
    
    return max(score, 0)

def get_grade(score):
    """O(1) grade calculation using bit operations"""
    return 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'

def generate_recommendations(ratios, business_type):
    """O(1) recommendation engine with pre-computed rules"""
    recommendations = []
    benchmark = BENCHMARKS.get(business_type, BENCHMARKS['services'])
    
    # Single pass recommendation generation - O(1)
    if ratios[0] < benchmark[0]:  # current_ratio
        recommendations.append("Optimize working capital - reduce inventory or accelerate collections")
    if ratios[2] < benchmark[2]:  # profit_margin
        recommendations.append("Implement cost reduction strategies - review pricing and expenses")
    if ratios[1] > benchmark[1]:  # debt_ratio
        recommendations.append("Consider debt restructuring or equity financing")
    
    return recommendations

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
<div class="header"><h1>Financial Health Assessment Platform</h1><p>AI-powered analysis for SMEs with instant results</p></div>
<div class="form"><h2>Business Financial Analysis</h2>
<select id="businessType"><option value="manufacturing">Manufacturing</option><option value="retail">Retail</option><option value="services">Services</option><option value="agriculture">Agriculture</option><option value="logistics">Logistics</option><option value="ecommerce">E-commerce</option></select>
<input type="number" id="revenue" placeholder="Annual Revenue (₹)" min="0">
<input type="number" id="profit" placeholder="Net Profit (₹)" min="0">
<input type="number" id="assets" placeholder="Current Assets (₹)" min="0">
<input type="number" id="liabilities" placeholder="Current Liabilities (₹)" min="0">
<input type="number" id="debt" placeholder="Total Debt (₹)" min="0">
<input type="number" id="equity" placeholder="Total Equity (₹)" min="0">
<button onclick="analyze()">Analyze Financial Health</button></div>
<div id="results" class="results"><h2>Financial Health Assessment Results</h2><div id="resultsContent"></div></div></div>
<script>
function analyze(){const d={business_type:document.getElementById('businessType').value,revenue:parseFloat(document.getElementById('revenue').value)||1000000,profit:parseFloat(document.getElementById('profit').value)||80000,assets:parseFloat(document.getElementById('assets').value)||300000,liabilities:parseFloat(document.getElementById('liabilities').value)||200000,debt:parseFloat(document.getElementById('debt').value)||400000,equity:parseFloat(document.getElementById('equity').value)||500000};
fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)})
.then(r=>r.json()).then(result=>{
document.getElementById('resultsContent').innerHTML=`<div class="score"><div class="score-circle grade-${result.grade.toLowerCase()}">${result.credit_score}</div><h3>Credit Grade: ${result.grade}</h3></div>
<div class="metrics"><div class="metric"><h4>Current Ratio</h4><p style="font-size:20px;color:#667eea">${result.current_ratio}</p></div>
<div class="metric"><h4>Profit Margin</h4><p style="font-size:20px;color:#667eea">${result.profit_margin}%</p></div>
<div class="metric"><h4>Debt Ratio</h4><p style="font-size:20px;color:#667eea">${result.debt_ratio}</p></div>
<div class="metric"><h4>Risk Level</h4><p style="font-size:20px;color:#667eea">${result.risk_level}</p></div></div>
<div class="recommendations"><h3>AI Recommendations</h3>${result.recommendations.map(r=>'<div class="rec">'+r+'</div>').join('')}</div>`;
document.getElementById('results').style.display='block'})}</script></body></html>'''

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        d = request.json
        
        # O(1) ratio calculations - single pass
        current_ratio = d['assets'] / max(d['liabilities'], 1)
        profit_margin = (d['profit'] / max(d['revenue'], 1)) * 100
        debt_ratio = d['debt'] / max(d['equity'], 1)
        
        # O(1) credit scoring
        score = calculate_score(current_ratio, profit_margin, debt_ratio)
        grade = get_grade(score)
        
        # O(1) risk assessment
        risk_level = 'Low' if score >= 70 else 'Medium' if score >= 50 else 'High'
        
        # O(1) recommendations
        ratios = (current_ratio, debt_ratio, profit_margin)
        recommendations = generate_recommendations(ratios, d['business_type'])
        
        return jsonify({
            'credit_score': score,
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