#!/usr/bin/env python
"""
Quick verification script for payroll admin functionality.
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'human_resources.settings')
django.setup()

from payroll.models import (
    PayrollConfiguration, PayrollPeriod, TaxBracket, 
    DeductionType, BonusType, Payslip, 
    PayslipDeduction, PayslipBonus, CompensationHistory
)
from django.contrib.admin.sites import site
from django.test import RequestFactory
from django.contrib.auth.models import User

def test_admin_models():
    """Test that all admin models are properly registered and accessible."""
    
    print("🔍 Testing Payroll Admin Interface")
    print("=" * 50)
    
    # Get all registered models
    payroll_models = [
        PayrollConfiguration, PayrollPeriod, TaxBracket, 
        DeductionType, BonusType, Payslip, 
        PayslipDeduction, PayslipBonus, CompensationHistory
    ]
    
    factory = RequestFactory()
    
    for model in payroll_models:
        model_name = model.__name__
        
        try:
            # Check if model is registered in admin
            admin_class = site._registry.get(model)
            if admin_class:
                print(f"✅ {model_name}: Admin registered")
                
                # Test list display
                if hasattr(admin_class, 'list_display'):
                    print(f"   📊 List display: {admin_class.list_display}")
                
                # Test if there are records
                count = model.objects.count()
                print(f"   📈 Records: {count}")
                
                # Test admin methods for CompensationHistory specifically
                if model == CompensationHistory and count > 0:
                    obj = model.objects.first()
                    try:
                        # Test the fixed methods
                        if hasattr(admin_class, 'salary_change'):
                            result = admin_class.salary_change(admin_class, obj)
                            print(f"   💰 Salary change method works: {result}")
                        
                        if hasattr(admin_class, 'previous_salary'):
                            result = admin_class.previous_salary(admin_class, obj)
                            print(f"   💵 Previous salary method works: {result}")
                            
                        if hasattr(admin_class, 'new_salary'):
                            result = admin_class.new_salary(admin_class, obj)
                            print(f"   💸 New salary method works: {result}")
                            
                    except Exception as e:
                        print(f"   ❌ Method error: {e}")
                
            else:
                print(f"❌ {model_name}: Not registered in admin")
                
        except Exception as e:
            print(f"❌ {model_name}: Error - {e}")
        
        print()
    
    print("🎯 Summary")
    print("=" * 50)
    
    total_registered = sum(1 for model in payroll_models if site._registry.get(model))
    print(f"Registered models: {total_registered}/{len(payroll_models)}")
    
    total_records = sum(model.objects.count() for model in payroll_models)
    print(f"Total records: {total_records}")
    
    if total_registered == len(payroll_models):
        print("✅ All payroll models are properly registered in admin!")
    else:
        print("❌ Some models are missing from admin registration")

if __name__ == "__main__":
    test_admin_models()
