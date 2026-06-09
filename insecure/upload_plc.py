"""
upload_plc.py
-------------
This script explores the available API endpoints on the OpenPLC Runtime
by testing a list of common endpoint names.

Purpose:
    During the project setup, the OpenPLC Runtime API documentation was
    not fully available. This script was written to discover which
    endpoints exist and how they respond, by sending GET requests to
    a list of candidate endpoint paths.

What it does:
    1. Authenticates with the OpenPLC Runtime API
    2. Sends a GET request to each candidate endpoint
    3. Prints the HTTP status code and response body for each

Findings from running this script:
    All endpoints returned HTTP 200 with {"error": "Unknown argument"}.
    This revealed that the Runtime uses a single dynamic route handler:
        GET /api/<command>
    where <command> is dispatched to a registered callback function.
    The valid commands are defined in app.py GET_HANDLERS dictionary.
"""

import requests
import urllib3

# Suppress SSL warnings from the self-signed certificate on OpenPLC Runtime
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime HTTPS API endpoint
BASE_URL = "https://127.0.0.1:8443"

# List of candidate API endpoint paths to test.
# These were common guesses based on typical REST API naming conventions.
CANDIDATE_ENDPOINTS = [
    "/api/programs",
    "/api/program",
    "/api/upload",
    "/api/plc",
]

# ─── Authentication ───────────────────────────────────────────────────────────

# Login to OpenPLC Runtime and retrieve a JWT access token
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,  # Accept self-signed TLS certificate
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("=" * 60)
print("  OpenPLC Runtime - API Endpoint Discovery")
print("=" * 60)
print(f"  Target : {BASE_URL}")
print(f"  Testing {len(CANDIDATE_ENDPOINTS)} candidate endpoints...")
print("=" * 60)

# ─── Endpoint Discovery ───────────────────────────────────────────────────────

for endpoint in CANDIDATE_ENDPOINTS:

    # Send a GET request to each candidate endpoint
    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=auth_headers,
        verify=False,
    )

    # Show the first 100 characters of the response body to keep output clean
    response_preview = response.text[:100]

    print(f"GET {endpoint}")
    print(f"  Status   : {response.status_code}")
    print(f"  Response : {response_preview}")
    print()

print("=" * 60)
print("  Discovery complete.")
print("  NOTE: All returned 'Unknown argument' -> Runtime uses")
print("  a single dynamic route: GET /api/<command>")
print("  Valid commands are defined in app.py GET_HANDLERS.")
print("=" * 60)
