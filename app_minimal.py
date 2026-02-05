from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial Health Assessment</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; border-radius: 10px; }
        .form { background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 10px; }
        input, select, button { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ddd; }
        button { background: #4CAF50; color: white; cursor: pointer; }
        .results { background: #e8f5e9; padding: 20px; border-radius: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Financial Health Assessment Platform</h1>
        <p>AI-powered analysis for SMEs</p>
    </div>
    
    <div class="form">
        <h2>Business Analysis</h2>
        <select id="businessType">
            <option value="manufacturing">Manufacturing</option>
            <option value="retail">Retail</option>
            <option value="services">Services</option>
            <option value="agriculture">Agriculture</option>
            <option value="logistics">Logistics</option>
            <option value="ecommerce">E-commerce</option>
        </select>
        
        <input type="number" id="revenue" placeholder="Annual Revenue" />
        <input type="number" id="profit" placeholder="Net Profit" />
        <input type="number" id="assets" placeholder="Current Assets" />
        <input type="number" id="liabilities" placeholder="Current Liabilities" />
        
        <button onclick="analyze()">Analyze Financial Health</button>
    </div>
    
    <div id="results" class="results" style="display:none;">
        <h2>Analysis Results</h2>
        <div id="resultsContent"></div>
    </div>

    <script>
        function analyze() {
            const data = {
                business_type: document.getElementById('businessType').value,
                revenue: parseFloat(document.getElementById('revenue').value) || 1000000,
                profit: parseFloat(document.getElementById('profit').value) || 80000,
                assets: parseFloat(document.getElementById('assets').value) || 300000,
                liabilities: parseFloat(document.getElementById('liabilities').value) || 200000
            };
            
            fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('resultsContent').innerHTML = `
                    <h3>Credit Score: ${result.credit_score} (Grade ${result.grade})</h3>
                    <p><strong>Current Ratio:</strong> ${result.current_ratio}</p>
                    <p><strong>Profit Margin:</strong> ${result.profit_margin}%</p>
                    <p><strong>Risk Level:</strong> ${result.risk_level}</p>
                    <h4>Recommendations:</h4>
                    <ul>${result.recommendations.map(r => '<li>' + r + '</li>').join('')}</ul>
                `;
                document.getElementById('results').style.display = 'block';
            });
        }
    </script>
</body>
</html>
    '''

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        
        # Calculate ratios
        current_ratio = data['assets'] / max(data['liabilities'], 1)
        profit_margin = (data['profit'] / max(data['revenue'], 1)) * 100
        
        # Credit scoring
        score = 100
        if current_ratio < 1.0:
            score -= 30
        if profit_margin < 5:
            score -= 20
        
        grade = 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'
        risk_level = 'Low' if score >= 70 else 'Medium' if score >= 50 else 'High'
        
        # Recommendations
        recommendations = []
        if current_ratio < 1.2:
            recommendations.append("Improve liquidity by reducing current liabilities")
        if profit_margin < 10:
            recommendations.append("Focus on cost optimization to improve profit margins")
        if score < 60:
            recommendations.append("Consider debt restructuring to improve financial health")
        
        return jsonify({
            'credit_score': max(score, 0),
            'grade': grade,
            'current_ratio': round(current_ratio, 2),
            'profit_margin': round(profit_margin, 2),
            'risk_level': risk_level,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)