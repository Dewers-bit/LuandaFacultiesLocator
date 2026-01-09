import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_login():
    print("Testing Login...")
    url = f"{BASE_URL}/api/login"
    
    # Test Invalid
    resp = requests.post(url, json={"username": "admin", "password": "wrongpassword"})
    if resp.status_code == 401:
        print("PASS: Invalid credentials rejected")
    else:
        print(f"FAIL: Invalid credentials not rejected (Status: {resp.status_code})")

    # Test Valid
    resp = requests.post(url, json={"username": "admin", "password": "password123"})
    if resp.status_code == 200 and resp.json().get("success"):
        print("PASS: Valid login successful")
        return resp.cookies
    else:
        print(f"FAIL: Valid login failed (Status: {resp.status_code})")
        sys.exit(1)

def test_institutions(cookies):
    print("Testing Institutions Data...")
    url = f"{BASE_URL}/api/institutions"
    resp = requests.get(url, cookies=cookies)
    
    if resp.status_code == 200:
        data = resp.json()
        if len(data) > 0:
            print(f"PASS: Retrieved {len(data)} institutions")
            print(f"First item: {data[0]['name']}")
        else:
            print("FAIL: No institutions found")
    else:
        print(f"FAIL: Failed to get institutions (Status: {resp.status_code})")

if __name__ == "__main__":
    time.sleep(2) # Give server time to start
    try:
        cookies = test_login()
        test_institutions(cookies)
        print("\nAll tests passed!")
    except Exception as e:
        print(f"Tests failed with error: {e}")
