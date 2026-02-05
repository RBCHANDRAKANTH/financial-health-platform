# Financial Health Assessment Platform

A comprehensive AI-powered financial health assessment platform for Small and Medium Enterprises (SMEs) that analyzes financial statements, cash flow patterns, and business metrics to provide actionable insights and recommendations.

## 🚀 Features

### Core Functionality
- **AI-Powered Financial Analysis** - Advanced algorithms analyze financial statements and provide intelligent insights
- **Credit Worthiness Assessment** - Automated credit scoring with industry benchmarking
- **Risk Assessment** - Comprehensive risk analysis across liquidity, credit, and operational dimensions
- **Financial Forecasting** - ML-based predictions for revenue, cash flow, and profitability
- **Industry Benchmarking** - Compare performance against industry standards

### Advanced Features
- **Automated Bookkeeping Assistance** - Smart categorization and analysis of financial transactions
- **Tax Compliance Checking** - GST compliance analysis and optimization suggestions
- **Working Capital Optimization** - Cash conversion cycle analysis and recommendations
- **Cost Optimization Strategies** - AI-driven cost reduction recommendations
- **Investor-Ready Reports** - Professional financial reports for stakeholders

### Integrations
- **Banking APIs** - Connect with HDFC, ICICI, SBI, and Axis Bank (up to 2 banks)
- **GST Integration** - Import GST filing data for compliance analysis
- **Payment Gateway Integration** - Razorpay and PayU integration for transaction analysis

### Multi-language Support
- English and Hindi interface
- Regional language support for business owners

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL with encryption
- **AI/ML**: OpenAI GPT, scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript, Plotly.js
- **Security**: AES encryption, secure API handling
- **File Processing**: pandas, openpyxl, PyPDF2

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API key
- Banking API credentials (optional)
- GST API access (optional)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd financial-health-assessment
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database setup**
```bash
# Create PostgreSQL database
createdb financial_health

# Run database schema
psql -d financial_health -f database_schema.sql
```

5. **Environment configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Generate encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

6. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📊 Usage

### 1. Upload Financial Documents
- Supported formats: CSV, XLSX, PDF
- Upload balance sheets, income statements, cash flow statements
- Select appropriate business type (Manufacturing, Retail, Services, etc.)

### 2. Financial Analysis
The platform automatically:
- Calculates key financial ratios
- Assesses creditworthiness
- Identifies risk factors
- Generates industry comparisons

### 3. View Results
- Interactive dashboard with financial metrics
- Credit score with grade (A-D)
- AI-powered recommendations
- Visual charts and graphs

### 4. Advanced Features
- Set up banking integrations for real-time data
- Configure GST integration for compliance analysis
- Generate investor reports
- Export analysis results

## 🔒 Security Features

- **Data Encryption**: All financial data encrypted at rest and in transit
- **Secure API Handling**: Banking credentials encrypted and securely stored
- **Audit Logging**: Complete audit trail of all financial data access
- **Regulatory Compliance**: Adheres to financial data protection standards

## 📈 Financial Metrics Analyzed

### Liquidity Ratios
- Current Ratio
- Quick Ratio
- Cash Ratio

### Profitability Ratios
- Gross Profit Margin
- Net Profit Margin
- Return on Assets (ROA)
- Return on Equity (ROE)

### Leverage Ratios
- Debt-to-Equity Ratio
- Debt-to-Assets Ratio
- Interest Coverage Ratio

### Efficiency Ratios
- Asset Turnover
- Inventory Turnover
- Receivables Turnover

### Working Capital Metrics
- Days Sales Outstanding (DSO)
- Days Inventory Outstanding (DIO)
- Days Payable Outstanding (DPO)
- Cash Conversion Cycle

## 🏭 Industry Support

The platform supports analysis for:
- Manufacturing
- Retail
- Services
- Agriculture
- Logistics
- E-commerce

Each industry has specific benchmarks and risk factors.

## 🔌 API Integrations

### Banking APIs
```python
# Example banking integration
banking_config = {
    'bank_name': 'hdfc',
    'credentials': {
        'api_key': 'your-api-key',
        'access_token': 'your-access-token',
        'account_id': 'your-account-id'
    }
}
```

### GST Integration
```python
# Example GST integration
gst_config = {
    'gstin': 'your-gstin',
    'username': 'your-username',
    'password': 'your-password',
    'app_key': 'your-app-key'
}
```

## 📊 Sample Data Format

### CSV Format
```csv
Date,Description,Amount,Category
2024-01-01,Sales Revenue,100000,Revenue
2024-01-01,Office Rent,-5000,Operating Expense
2024-01-01,Raw Materials,-30000,Cost of Goods Sold
```

### Financial Statement Format
```csv
Account,Amount,Type
Current Assets,500000,Asset
Current Liabilities,300000,Liability
Revenue,1000000,Income
Net Income,80000,Income
```

## 🚨 Error Handling

The platform includes comprehensive error handling for:
- Invalid file formats
- Missing financial data
- API connection failures
- Database errors
- Encryption/decryption issues

## 📝 API Endpoints

### Core Endpoints
- `POST /api/upload` - Upload financial documents
- `GET /api/assessment/<id>` - Retrieve assessment results
- `POST /api/ai-insights` - Get AI-powered insights
- `POST /api/forecast` - Generate financial forecasts

### Integration Endpoints
- `POST /api/banking/connect` - Connect banking API
- `POST /api/gst/sync` - Sync GST data
- `GET /api/compliance/status` - Check compliance status

## 🔧 Configuration

### Database Configuration
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'financial_health',
    'user': 'postgres',
    'password': 'your-password'
}
```

### AI Configuration
```python
AI_CONFIG = {
    'provider': 'openai',
    'model': 'gpt-3.5-turbo',
    'max_tokens': 1000,
    'temperature': 0.7
}
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📈 Performance Optimization

- Database indexing for fast queries
- Caching for frequently accessed data
- Async processing for large file uploads
- Connection pooling for database operations

## 🛡️ Compliance

The platform ensures:
- GDPR compliance for data protection
- SOX compliance for financial reporting
- Industry-specific regulatory requirements
- Audit trail maintenance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@financialhealth.com
- Documentation: [docs.financialhealth.com]
- Issues: GitHub Issues

## 🔄 Updates and Roadmap

### Current Version: 1.0.0
- Core financial analysis
- Basic integrations
- Multi-language support

### Upcoming Features
- Advanced ML models
- More banking integrations
- Mobile application
- Real-time monitoring
- Advanced reporting

## ⚠️ Important Notes

1. **Security**: Never commit actual API keys or credentials to version control
2. **Data Privacy**: All financial data is encrypted and handled securely
3. **Compliance**: Ensure proper regulatory compliance in your jurisdiction
4. **Testing**: Test thoroughly with sample data before using with real financial information
5. **Backup**: Regular database backups are essential for production use

## 📚 Additional Resources

- [Financial Ratio Analysis Guide](docs/financial-ratios.md)
- [API Integration Tutorial](docs/api-integration.md)
- [Security Best Practices](docs/security.md)
- [Troubleshooting Guide](docs/troubleshooting.md)