"""
plc_bridge.py
-------------
This is the INSECURE version of the PLC data bridge script.

Role in the system:
    This script acts as a bridge between the OpenPLC Runtime and the
    Flask data receiver server. It:
        1. Authenticates with the OpenPLC Runtime via HTTPS
        2. Reads the current PLC status every 2 seconds
        3. Simulates PLC sensor values (temperature, alarms, etc.)
        4. Forwards the data to the Flask server over HTTP (INSECURE)

Security concern:
    While the connection TO the OpenPLC Runtime uses HTTPS (encrypted),
    the connection FROM this bridge TO the Flask server uses plain HTTP.
    This means all PLC data is transmitted without encryption and can be
    captured by Wireshark or any network sniffer.

This represents the "before security" scenario in the project demo.
"""

import random
import time

import requests
import urllib3

# Suppress SSL warnings from the self-signed certificate on OpenPLC Runtime
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime API (uses HTTPS with self-signed certificate)
PLC_URL = "https://127.0.0.1:8443"

# Flask data receiver server (uses plain HTTP - INSECURE)
FLASK_URL = "http://127.0.0.1:5000"

# Polling interval in seconds between each data collection cycle
POLL_INTERVAL = 2

# ─── Authentication ───────────────────────────────────────────────────────────

# Authenticate with the OpenPLC Runtime REST API to get a JWT access token.
# The Runtime uses HTTPS so this credential exchange is encrypted.
login_response = requests.post(
    f"{PLC_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,  # Accept self-signed TLS certificate
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("=" * 55)
print("  PLC Data Bridge - INSECURE (HTTP) MODE")
print("=" * 55)
print(f"  PLC Source  : {PLC_URL} (HTTPS - encrypted)")
print(f"  Destination : {FLASK_URL} (HTTP - NOT encrypted)")
print("  WARNING: PLC data is sent as plain text to Flask!")
print("=" * 55)

# ─── Main Data Loop ───────────────────────────────────────────────────────────

cycle = 0

while True:
    cycle += 1

    # ── Read PLC Status ───────────────────────────────────────────────────────

    # Query the OpenPLC Runtime for the current PLC execution status.
    # Possible values: STATUS:RUNNING, STATUS:STOPPED, STATUS:EMPTY
    status_response = requests.get(
        f"{PLC_URL}/api/status",
        headers=auth_headers,
        verify=False,
    )
    plc_status = status_response.json().get("status", "UNKNOWN")

    # ── Simulate PLC Sensor Data ──────────────────────────────────────────────

    # Note: The OpenPLC Runtime does not expose individual variable values
    # through its REST API (only status and logs). In a real deployment,
    # this would use Modbus TCP to read registers directly from the PLC.
    # For this demonstration, we simulate realistic sensor values that
    # reflect the control logic written in the PLC program (POUS.inc).

    # Simulate temperature sensor reading (Celsius)
    temp = random.randint(20, 80)

    # Build the data payload that mirrors the PLC program variables:
    #   heater_on      -> True when temperature < 50 (heater keeping temp up)
    #   alarm_high     -> True when temperature > 70 (high limit threshold)
    #   alarm_critical -> True when temperature > 85 (critical limit threshold)
    #   system_ok      -> True when no critical alarm is active
    data = {
        "cycle": cycle,
        "plc_status": plc_status,
        "temperature": temp,
        "heater_on": temp < 50,
        "alarm_high": temp > 70,
        "alarm_critical": temp > 85,
        "system_ok": temp <= 85,
    }

    # ── Send to Flask Server (INSECURE - HTTP) ────────────────────────────────

    # This POST request is sent over plain HTTP with NO encryption.
    # The full JSON payload (including sensor readings and alarm states)
    # is visible in Wireshark as readable text — this is the vulnerability
    # we are demonstrating in this project.
    response = requests.post(
        f"{FLASK_URL}/plc-data",
        json=data,
    )

    # Print cycle summary to console
    alarm_flag = "ALARM!" if data["alarm_high"] else "OK"
    print(
        f"[Cycle {cycle:>3}] "
        f"Temp={temp:>3}C | "
        f"Heater={'ON ' if data['heater_on'] else 'OFF'} | "
        f"Status={alarm_flag} | "
        f"PLC={plc_status} | "
        f"Sent={response.json().get('status', 'error')}"
    )

    # Wait before next cycle
    time.sleep(POLL_INTERVAL)
