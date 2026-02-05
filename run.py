#!/usr/bin/env python3
"""
Financial Health Assessment Platform - Startup Script
This script initializes the database and starts the Flask application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import pandas
        import psycopg2
        import openai
        import cryptography
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set"""
    required_vars = ['SECRET_KEY', 'DB_NAME', 'ENCRYPTION_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please copy .env.example to .env and configure your settings")
        return False
    
    print("✓ Environment variables configured")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs', 'backups']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_database():
    """Initialize database with schema"""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Database connection parameters
        db_params = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', 'password'),
            'port': os.environ.get('DB_PORT', '5432')
        }
        
        db_name = os.environ.get('DB_NAME', 'financial_health')
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Created database: {db_name}")
        else:
            print(f"✓ Database {db_name} already exists")
        
        cur.close()
        conn.close()
        
        # Connect to the application database and run schema
        db_params['database'] = db_name
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Check if tables exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'businesses'
        """)
        
        if not cur.fetchone():
            # Run database schema
            with open('database_schema.sql', 'r') as f:
                schema_sql = f.read()
                cur.execute(schema_sql)
                conn.commit()
                print("✓ Database schema initialized")
        else:
            print("✓ Database schema already exists")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def generate_sample_config():
    """Generate sample configuration if .env doesn't exist"""
    if not os.path.exists('.env'):
        print("Generating sample .env file...")
        
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        
        sample_env = f"""# Financial Health Assessment Platform Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development

# Database Configuration
DB_HOST=localhost
DB_NAME=financial_health
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432

# Encryption Key
ENCRYPTION_KEY={encryption_key}

# OpenAI API (Optional - for AI insights)
OPENAI_API_KEY=your-openai-api-key-here

# Development Settings
DEBUG=True
"""
        
        with open('.env', 'w') as f:
            f.write(sample_env)
        
        print("✓ Created .env file with sample configuration")
        print("Please update the .env file with your actual configuration")

def main():
    """Main startup function"""
    print("🚀 Starting Financial Health Assessment Platform...")
    print("=" * 50)
    
    # Load environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Loaded environment variables from .env")
    else:
        generate_sample_config()
        from dotenv import load_dotenv
        load_dotenv()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        print("⚠️  Database initialization failed, but continuing...")
    
    # Start the Flask application
    print("\n" + "=" * 50)
    print("🌟 Starting Flask application...")
    print("📊 Financial Health Assessment Platform")
    print("🔗 Access the application at: http://localhost:5000")
    print("=" * 50)
    
    try:
        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=os.environ.get('DEBUG', 'True').lower() == 'true'
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()