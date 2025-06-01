#!/usr/bin/env python
"""
Simple test script for Payroll Management System
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

print("🚀 Testing Payroll Management System...")

try:
    import requests
    print("✅ Requests module loaded")
    
    from django.contrib.auth import get_user_model
    from rest_framework.authtoken.models import Token
    print("✅ Django modules loaded")
    
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    print(f"✅ Found superuser: {user.username}")
    
    token, created = Token.objects.get_or_create(user=user)
    print(f"✅ Token obtained: {token.key[:10]}...")
    
    # Test basic API call
    headers = {'Authorization': f'Token {token.key}'}
    response = requests.get('http://127.0.0.1:8000/api/payroll/payslips/', headers=headers)
    print(f"✅ API Test: {response.status_code} - {len(response.json()) if response.status_code == 200 else 'Error'}")
    
    from payroll.models import Payslip, PayrollPeriod
    print(f"✅ Database: {Payslip.objects.count()} payslips, {PayrollPeriod.objects.count()} periods")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("🎉 Simple test complete!")
