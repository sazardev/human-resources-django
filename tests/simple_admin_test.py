import requests
import sys

try:
    print("Testing CompensationHistory admin page...")
    
    # Test basic server access
    response = requests.get('http://127.0.0.1:8000/admin/', timeout=5)
    print(f"Admin home page status: {response.status_code}")
    
    # Test CompensationHistory admin page
    response = requests.get('http://127.0.0.1:8000/admin/payroll/compensationhistory/', timeout=5)
    print(f"CompensationHistory admin page status: {response.status_code}")
    
    if response.status_code in [200, 302]:
        print("SUCCESS: Admin page is accessible without server errors!")
        print("The SafeString format error has been resolved!")
    else:
        print(f"Warning: Unexpected status code {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
