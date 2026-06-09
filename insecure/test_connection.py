"""
test_connection.py
------------------
This script tests the connection to the OpenPLC Runtime API and verifies
that authentication is working correctly.

Purpose:
    A simple diagnostic script used to:
        1. Confirm the OpenPLC Runtime is reachable on port 8443
        2. Verify that the admin credentials are correct
        3. Check the current PLC execution status

This was the first script written during the project setup phase
to confirm that Python can communicate with the OpenPLC Runtime API.

Expected output (if everything is working):
    Login status: 200
    Response: {'access_token': 'eyJhbGci...'}
    LOGIN SUCCESS!
    PLC Status: {'status': 'STATUS:RUNNING'}
"""

import requests
import urllib3

# Suppress SSL warnings caused by the self-signed certificate on OpenPLC Runtime.
# In production, a proper CA-signed certificate should be used instead.
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime HTTPS API endpoint
BASE_URL = "https://127.0.0.1:8443"

# Admin credentials for the OpenPLC Runtime
# (password was reset using reset_password.py during project setup)
USERNAME = "admin"
PASSWORD = "admin123"

# ─── Step 1: Test Authentication ──────────────────────────────────────────────

print("=" * 50)
print("  OpenPLC Runtime - Connection Test")
print("=" * 50)
print(f"  Target : {BASE_URL}")
print(f"  User   : {USERNAME}")
print("=" * 50)
print("\n[1/2] Testing authentication...")

# Send login request to the OpenPLC Runtime API.
# The Runtime responds with a JWT access token if credentials are valid.
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": USERNAME, "password": PASSWORD},
    verify=False,  # Accept self-signed TLS certificate
)

print(f"  HTTP Status : {login_response.status_code}")
print(f"  Response    : {login_response.json()}")

# ─── Step 2: Read PLC Status (if authenticated) ───────────────────────────────

if login_response.status_code == 200:
    # Extract the JWT access token from the login response
    token = login_response.json().get("access_token")

    print(f"\n✅ LOGIN SUCCESS!")
    print(f"  Token (first 50 chars): {token[:50]}...")

    # All authenticated API calls require the token in the Authorization header
    auth_headers = {"Authorization": f"Bearer {token}"}

    print("\n[2/2] Reading PLC status...")

    # Query the current PLC execution state
    # Possible responses:
    #   STATUS:RUNNING -> PLC program is actively executing
    #   STATUS:STOPPED -> PLC is loaded but not running
    #   STATUS:EMPTY   -> No PLC program has been loaded
    status_response = requests.get(
        f"{BASE_URL}/api/status",
        headers=auth_headers,
        verify=False,
    )
    plc_status = status_response.json()
    print(f"  PLC Status : {plc_status}")

    print("\n" + "=" * 50)
    print("  Connection test PASSED.")
    print("=" * 50)

else:
    # Authentication failed — common causes:
    #   - Wrong username or password
    #   - OpenPLC Runtime is not running
    #   - Network/firewall issue
    print(f"\n❌ LOGIN FAILED!")
    print(f"  HTTP Status : {login_response.status_code}")
    print(f"  Reason      : {login_response.json()}")
    print("\n  Possible causes:")
    print("  - Wrong username or password")
    print("  - OpenPLC Runtime is not running")
    print("  - Check that the Runtime is started before running this script")
