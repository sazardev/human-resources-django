"""
Test API endpoints using requests library
"""
import requests
import json

def test_attendance_api():
    """Test attendance API endpoints."""
    base_url = "http://127.0.0.1:8000/api/attendance"
    
    print("=== Testing Attendance API Endpoints ===")
    
    # Test endpoints
    endpoints = [
        "/schedules/",
        "/time-entries/", 
        "/timesheets/",
        "/overtime-requests/",
        "/reports/"
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            print(f"GET {url}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  Found {len(data)} items")
                elif isinstance(data, dict) and 'results' in data:
                    print(f"  Found {len(data['results'])} items (paginated)")
                else:
                    print(f"  Response type: {type(data)}")
            elif response.status_code == 401:
                print("  Authentication required")
            elif response.status_code == 403:
                print("  Access forbidden") 
            else:
                print(f"  Error: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  Connection failed - server may not be running")
        except requests.exceptions.Timeout:
            print(f"  Request timed out")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test with filters
    print("\n=== Testing WorkSchedule Filters ===")
    schedule_url = base_url + "/schedules/"
    
    test_params = [
        {"department": 1},
        {"is_active": "true"},
        {"schedule_type": "fixed"},
        {"search": "schedule"}
    ]
    
    for params in test_params:
        try:
            response = requests.get(schedule_url, params=params, timeout=5)
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            print(f"GET {schedule_url}?{param_str}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  Connection failed")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_attendance_api()
