#!/usr/bin/env python
"""
Test script for Payroll Management System
This script verifies that all major payroll endpoints are working correctly
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

import requests
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from payroll.models import PayrollPeriod, Payslip, TaxBracket, DeductionType, BonusType

User = get_user_model()

def get_auth_token():
    """Get or create authentication token for testing"""
    try:
        # Try to get existing admin user
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("❌ No superuser found. Please create one with: python manage.py createsuperuser")
            return None
        
        token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"✅ Created new auth token for user: {user.username}")
        else:
            print(f"✅ Using existing auth token for user: {user.username}")
        
        return token.key
    except Exception as e:
        print(f"❌ Error getting auth token: {e}")
        return None

def test_endpoint(url, token, description):
    """Test a single API endpoint"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 'N/A')
            print(f"✅ {description}: {response.status_code} - {count} items")
            return True
        else:
            print(f"❌ {description}: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)[:100]}")
        return False

def main():
    print("🚀 Testing Payroll Management System...")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return
    
    base_url = "http://127.0.0.1:8000/api/payroll"
    
    # Test all major endpoints
    endpoints = [
        (f"{base_url}/payroll-periods/", "Payroll Periods"),
        (f"{base_url}/payslips/", "Payslips"),
        (f"{base_url}/tax-brackets/", "Tax Brackets"),
        (f"{base_url}/deduction-types/", "Deduction Types"),
        (f"{base_url}/bonus-types/", "Bonus Types"),
        (f"{base_url}/compensation-history/", "Compensation History"),
        (f"{base_url}/payroll-configuration/", "Payroll Configuration"),
        (f"{base_url}/analytics/", "Payroll Analytics"),
    ]
    
    successful_tests = 0
    total_tests = len(endpoints)
    
    print("\n📊 Testing API Endpoints:")
    print("-" * 30)
    
    for url, description in endpoints:
        if test_endpoint(url, token, description):
            successful_tests += 1
    
    print("\n" + "=" * 50)
    print(f"✅ {successful_tests}/{total_tests} endpoints working correctly")
    
    # Test database content
    print("\n📈 Database Summary:")
    print("-" * 20)
    print(f"Payroll Periods: {PayrollPeriod.objects.count()}")
    print(f"Payslips: {Payslip.objects.count()}")
    print(f"Tax Brackets: {TaxBracket.objects.count()}")
    print(f"Deduction Types: {DeductionType.objects.count()}")
    print(f"Bonus Types: {BonusType.objects.count()}")
    
    # Test specific API actions
    print("\n🎯 Testing Specific Features:")
    print("-" * 30)
    
    # Test payroll period summary
    period = PayrollPeriod.objects.first()
    if period:
        summary_url = f"{base_url}/payroll-periods/{period.id}/summary/"
        test_endpoint(summary_url, token, "Payroll Period Summary")
    
    # Test configuration endpoint
    config_url = f"{base_url}/payroll-configuration/current/"
    test_endpoint(config_url, token, "Current Configuration")
    
    print("\n🎉 Payroll Management System Test Complete!")
    print("💡 Access the admin interface at: http://127.0.0.1:8000/admin/")
    print("🔗 API documentation available in DRF browsable API")

if __name__ == "__main__":
    main()
