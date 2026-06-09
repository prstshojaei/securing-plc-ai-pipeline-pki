"""
plc_bridge_secure.py
--------------------
This is the SECURE version of the PLC data bridge script.

Both connections are now encrypted:
    - OpenPLC Runtime : HTTPS port 8443 (encrypted)
    - Flask Server    : HTTPS port 5443 (encrypted)

This represents the "after security" scenario where TLS/PKI
protects the entire data pipeline from end to end.
"""
import os

os.environ["SSLKEYLOGFILE"] = (
    r"E:\Parastoo\STU\Uni\Msc\2\Internet Security\Project\with OPENPLC - C\code\secure\sslkeys.log"
)

import random
import time
import requests
import urllib3

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime API (HTTPS)
PLC_URL = "https://127.0.0.1:8443"

# Flask secure server (HTTPS - encrypted)
FLASK_URL = "https://127.0.0.1:5443"

# Path to the self-signed certificate for verification
CERT_FILE = "cert.pem"

# Polling interval in seconds
POLL_INTERVAL = 2

# ─── Authentication ───────────────────────────────────────────────────────────

login_response = requests.post(
    f"{PLC_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("=" * 55)
print("  PLC Data Bridge - SECURE (HTTPS/TLS) MODE")
print("=" * 55)
print(f"  PLC Source  : {PLC_URL} (HTTPS - encrypted)")
print(f"  Destination : {FLASK_URL} (HTTPS - encrypted)")
print(f"  Certificate : {CERT_FILE}")
print("  All traffic is TLS encrypted end-to-end!")
print("=" * 55)

# ─── Main Data Loop ───────────────────────────────────────────────────────────

cycle = 0

while True:
    cycle += 1

    # Read PLC status from OpenPLC Runtime
    status_response = requests.get(
        f"{PLC_URL}/api/status",
        headers=auth_headers,
        verify=False,
    )
    plc_status = status_response.json().get("status", "UNKNOWN")

    # Simulate PLC sensor data
    temp = random.randint(20, 80)

    data = {
        "cycle": cycle,
        "plc_status": plc_status,
        "temperature": temp,
        "heater_on": temp < 50,
        "alarm_high": temp > 70,
        "alarm_critical": temp > 85,
        "system_ok": temp <= 85,
    }

    # Send to Flask Server over HTTPS (SECURE - TLS encrypted)
    # verify=CERT_FILE tells requests to verify the server certificate
    
    response = requests.post(
        f"{FLASK_URL}/plc-data",
        json=data,
        verify=CERT_FILE,  # Verify server identity using our certificate
    )

    alarm_flag = "ALARM!" if data["alarm_high"] else "OK"
    print(
        f"[Cycle {cycle:>3}] "
        f"Temp={temp:>3}C | "
        f"Heater={'ON ' if data['heater_on'] else 'OFF'} | "
        f"Status={alarm_flag} | "
        f"Sent={response.json().get('status')} 🔒"
    )

    time.sleep(POLL_INTERVAL)
