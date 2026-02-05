-- Financial Health Assessment Database Schema

-- Create database
CREATE DATABASE financial_health;

-- Use the database
\c financial_health;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Businesses table
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    registration_number VARCHAR(100),
    gst_number VARCHAR(15),
    contact_email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial assessments table
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    business_type VARCHAR(100) NOT NULL,
    assessment_date DATE DEFAULT CURRENT_DATE,
    encrypted_data BYTEA NOT NULL, -- Encrypted financial data
    credit_score INTEGER,
    credit_grade VARCHAR(2),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial documents table
CREATE TABLE financial_documents (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    assessment_id INTEGER REFERENCES assessments(id),
    document_type VARCHAR(50) NOT NULL, -- 'balance_sheet', 'income_statement', 'cash_flow'
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    encrypted_content BYTEA, -- Encrypted document content
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial metrics table
CREATE TABLE financial_metrics (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_category VARCHAR(50), -- 'liquidity', 'profitability', 'leverage', 'efficiency'
    benchmark_value DECIMAL(15,2),
    industry_percentile INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL, -- 'High', 'Medium', 'Low'
    recommendation TEXT NOT NULL,
    implementation_timeline VARCHAR(50),
    expected_impact TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Banking integrations table
CREATE TABLE banking_integrations (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    bank_name VARCHAR(100) NOT NULL,
    account_number_encrypted BYTEA, -- Encrypted account number
    api_credentials_encrypted BYTEA, -- Encrypted API credentials
    integration_status VARCHAR(20) DEFAULT 'active',
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GST data table
CREATE TABLE gst_data (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    filing_period VARCHAR(20) NOT NULL, -- 'GSTR1-202310'
    turnover DECIMAL(15,2),
    tax_liability DECIMAL(15,2),
    input_tax_credit DECIMAL(15,2),
    net_tax_payable DECIMAL(15,2),
    filing_status VARCHAR(20),
    encrypted_details BYTEA, -- Encrypted GST return details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table for security
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    business_id INTEGER REFERENCES businesses(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Industry benchmarks table
CREATE TABLE industry_benchmarks (
    id SERIAL PRIMARY KEY,
    industry VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    benchmark_value DECIMAL(10,4),
    percentile_25 DECIMAL(10,4),
    percentile_50 DECIMAL(10,4),
    percentile_75 DECIMAL(10,4),
    data_source VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry, metric_name)
);

-- Financial forecasts table
CREATE TABLE financial_forecasts (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES assessments(id),
    forecast_period VARCHAR(20) NOT NULL, -- 'Q1-2024', 'FY-2024'
    forecast_type VARCHAR(50) NOT NULL, -- 'revenue', 'cash_flow', 'profit'
    predicted_value DECIMAL(15,2),
    confidence_interval_lower DECIMAL(15,2),
    confidence_interval_upper DECIMAL(15,2),
    model_accuracy DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_assessments_business_id ON assessments(business_id);
CREATE INDEX idx_assessments_date ON assessments(assessment_date);
CREATE INDEX idx_financial_metrics_assessment ON financial_metrics(assessment_id);
CREATE INDEX idx_recommendations_assessment ON recommendations(assessment_id);
CREATE INDEX idx_audit_logs_business ON audit_logs(business_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- Insert sample industry benchmarks
INSERT INTO industry_benchmarks (industry, metric_name, benchmark_value, percentile_25, percentile_50, percentile_75) VALUES
('manufacturing', 'current_ratio', 1.50, 1.20, 1.50, 1.80),
('manufacturing', 'debt_to_equity', 0.60, 0.40, 0.60, 0.80),
('manufacturing', 'profit_margin', 0.08, 0.05, 0.08, 0.12),
('retail', 'current_ratio', 1.20, 1.00, 1.20, 1.40),
('retail', 'debt_to_equity', 0.80, 0.60, 0.80, 1.00),
('retail', 'profit_margin', 0.05, 0.03, 0.05, 0.08),
('services', 'current_ratio', 1.30, 1.10, 1.30, 1.50),
('services', 'debt_to_equity', 0.50, 0.30, 0.50, 0.70),
('services', 'profit_margin', 0.12, 0.08, 0.12, 0.18),
('agriculture', 'current_ratio', 1.40, 1.20, 1.40, 1.60),
('agriculture', 'debt_to_equity', 0.70, 0.50, 0.70, 0.90),
('agriculture', 'profit_margin', 0.06, 0.04, 0.06, 0.10),
('logistics', 'current_ratio', 1.10, 0.90, 1.10, 1.30),
('logistics', 'debt_to_equity', 0.90, 0.70, 0.90, 1.10),
('logistics', 'profit_margin', 0.04, 0.02, 0.04, 0.07),
('ecommerce', 'current_ratio', 1.60, 1.40, 1.60, 1.80),
('ecommerce', 'debt_to_equity', 0.40, 0.20, 0.40, 0.60),
('ecommerce', 'profit_margin', 0.10, 0.06, 0.10, 0.15);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();