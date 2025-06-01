import requests
import json

print("🔐 Testing admin login...")
data = {'email': 'admin@admin.com', 'password': 'admin'}
response = requests.post('http://localhost:8000/api/auth/login/', json=data)

if response.status_code == 200:
    token = response.json().get('token')
    print(f"✅ Admin token obtained: {token[:20]}...")
    
    # Test session management endpoint
    print("📊 Testing session management endpoint...")
    headers = {'Authorization': f'Token {token}'}
    session_response = requests.get('http://localhost:8000/api/auth/admin/sessions/', headers=headers)
    
    print(f"Session endpoint status: {session_response.status_code}")
    if session_response.status_code == 200:
        result = session_response.json()
        sessions = result.get('sessions', [])
        print(f"✅ Found {len(sessions)} sessions")
        
        for i, session in enumerate(sessions):
            if i >= 5:  # Limit to first 5
                break
            user = session.get('user', 'Unknown')
            active = session.get('is_active', False)
            started = session.get('started_at', 'Unknown')
            ended = session.get('ended_at', 'Still active')
            duration = session.get('duration', 'N/A')
            
            print(f"  Session {i+1}:")
            print(f"    User: {user}")
            print(f"    Active: {'🟢' if active else '🔴'} {active}")
            print(f"    Started: {started}")
            print(f"    Ended: {ended}")
            print(f"    Duration: {duration}")
            print()
    else:
        print(f"❌ Session endpoint error: {session_response.text}")
else:
    print(f"❌ Admin login failed: {response.text}")
