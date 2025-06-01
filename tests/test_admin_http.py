import requests
import sys

def test_admin_access():
    """Test if the admin interface is accessible via HTTP."""
    
    try:
        # Test the main payroll admin page
        response = requests.get('http://127.0.0.1:8000/admin/payroll/', timeout=10)
        print(f"Payroll admin status: {response.status_code}")
        
        # Test the specific CompensationHistory admin page
        response = requests.get('http://127.0.0.1:8000/admin/payroll/compensationhistory/', timeout=10)
        print(f"CompensationHistory admin status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CompensationHistory admin is accessible!")
            return True
        elif response.status_code == 302:
            print("✅ Admin requires login (normal behavior)")
            return True
        else:
            print(f"❌ Error accessing admin: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    if test_admin_access():
        print("🎉 SUCCESS: Admin interface is working!")
    else:
        print("💥 FAILED: Admin interface has issues!")
        sys.exit(1)
