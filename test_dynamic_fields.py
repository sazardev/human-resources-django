#!/usr/bin/env python
"""
Test script for Dynamic Field Selection API

This script demonstrates various ways to use the dynamic field selection feature
of the Human Resources API. Run this after starting the Django development server.

Requirements:
- Django development server running on http://localhost:8000
- Sample data in the database
- Authentication token (update the AUTH_TOKEN variable below)
"""

import requests
import json
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000/api/"
AUTH_TOKEN = "ade3905bafe2b658fd65ec215d222c2c812c5642"  # Replace with actual token

headers = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def make_request(endpoint, params=None):
    """Make API request and return response"""
    url = urljoin(BASE_URL, endpoint)
    try:
        response = requests.get(url, headers=headers, params=params or {})
        return response
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    
    if response is None:
        print("❌ Request failed")
        return
        
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response size: {len(response.content)} bytes")
            print("Response data:")
            print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
    else:
        print(f"❌ Error: {response.text}")

def test_basic_field_selection():
    """Test basic field selection"""
    print_response(
        "Basic Field Selection - Employee ID, Name, Email only",
        make_request("employees/", {"fields": "id,first_name,last_name,email"})
    )

def test_field_exclusion():
    """Test field exclusion"""
    print_response(
        "Field Exclusion - Exclude sensitive fields",
        make_request("employees/", {"exclude": "salary,address,phone"})
    )

def test_nested_field_selection():
    """Test nested field selection"""
    print_response(
        "Nested Field Selection - Employee with Department name only",
        make_request("employees/", {"fields": "id,first_name,last_name,department.name,user.email"})
    )

def test_performance_review_fields():
    """Test performance review field selection"""
    print_response(
        "Performance Reviews - Rating and Employee info",
        make_request("performance-reviews/", {
            "fields": "id,overall_rating,review_date,employee.first_name,employee.last_name,employee.department.name"
        })
    )

def test_performance_goals_fields():
    """Test performance goals field selection"""
    print_response(
        "Performance Goals - Status and progress tracking",
        make_request("performance-goals/", {
            "fields": "id,title,status,progress_percentage,target_date,employee.first_name,employee.last_name"
        })
    )

def test_department_with_field_selection():
    """Test department field selection"""
    print_response(
        "Departments - Name only",
        make_request("departments/", {"fields": "id,name"})
    )

def test_combined_with_filters():
    """Test field selection combined with filters"""
    print_response(
        "Combined with Filters - Active employees with basic info",
        make_request("employees/", {
            "fields": "id,first_name,last_name,department.name",
            "employment_status": "active"
        })
    )

def test_full_vs_minimal_comparison():
    """Compare full response vs minimal response"""
    # Full response
    full_response = make_request("employees/")
    print_response("Full Employee Response", full_response)
    
    # Minimal response
    minimal_response = make_request("employees/", {"fields": "id,first_name,last_name"})
    print_response("Minimal Employee Response", minimal_response)
      # Size comparison
    if full_response and minimal_response and full_response.status_code == 200 and minimal_response.status_code == 200:
        full_size = len(full_response.content)
        minimal_size = len(minimal_response.content)
        reduction = ((full_size - minimal_size) / full_size) * 100
        
        print(f"\n{'='*60}")
        print("SIZE COMPARISON")
        print(f"{'='*60}")
        print(f"Full response: {full_size} bytes")
        print(f"Minimal response: {minimal_size} bytes")
        print(f"Size reduction: {reduction:.1f}%")

def test_invalid_fields():
    """Test handling of invalid field names"""
    print_response(
        "Invalid Field Names - Should ignore invalid fields gracefully",
        make_request("employees/", {"fields": "id,invalid_field,first_name,another_invalid"})
    )

def run_all_tests():
    """Run all dynamic field selection tests"""
    print("🚀 Starting Dynamic Field Selection API Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Basic tests
    test_basic_field_selection()
    test_field_exclusion()
    test_nested_field_selection()
    
    # Model-specific tests
    test_performance_review_fields()
    test_performance_goals_fields()
    test_department_with_field_selection()
    
    # Advanced tests
    test_combined_with_filters()
    test_full_vs_minimal_comparison()
    test_invalid_fields()
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running")
    except requests.RequestException:
        print("❌ Server is not running. Please start the Django development server:")
        print("   python manage.py runserver")
        exit(1)
    
    # Update auth token warning
    if AUTH_TOKEN == "your-auth-token-here":
        print("⚠️  Warning: Update the AUTH_TOKEN variable with a valid token")
        print("   You can get a token by creating a user and using the token authentication endpoint")
        print("   For testing without auth, you may need to temporarily disable authentication")
        print()
    
    run_all_tests()
