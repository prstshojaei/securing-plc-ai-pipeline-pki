"""
read_plc.py
-----------
This script connects to the OpenPLC Runtime API and reads live data
from the running PLC system.

Purpose:
    Used to verify that the OpenPLC Runtime is running correctly and
    to inspect the PLC execution status and runtime log messages.
    This is a diagnostic/testing script used during development.

What it reads:
    - PLC execution status (RUNNING, STOPPED, EMPTY)
    - Runtime log messages (INFO, WARNING, ERROR events)

Note:
    This script only reads STATUS and LOGS from the API.
    Individual PLC variable values (temperature, alarms, etc.)
    are not accessible via the REST API — those require Modbus TCP.
"""

import time

import requests
import urllib3

# Suppress SSL warnings from the self-signed certificate on OpenPLC Runtime
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime HTTPS API endpoint
BASE_URL = "https://127.0.0.1:8443"

# Number of read cycles to perform before the script exits
READ_CYCLES = 5

# Delay between each read cycle (seconds)
READ_INTERVAL = 2

# ─── Authentication ───────────────────────────────────────────────────────────

# Login to OpenPLC Runtime and retrieve a JWT access token.
# All subsequent API calls require this token in the Authorization header.
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,  # Accept self-signed TLS certificate
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("=" * 50)
print("  OpenPLC Runtime - Live Data Reader")
print("=" * 50)
print(f"  Connected to : {BASE_URL}")
print(f"  Read cycles  : {READ_CYCLES}")
print(f"  Interval     : {READ_INTERVAL}s")
print("=" * 50)

# ─── Read Loop ────────────────────────────────────────────────────────────────

for i in range(READ_CYCLES):

    # ── Read PLC Status ───────────────────────────────────────────────────────

    # Query the current PLC execution state.
    # Possible responses:
    #   STATUS:RUNNING  -> PLC program is actively executing scan cycles
    #   STATUS:STOPPED  -> PLC is loaded but not running
    #   STATUS:EMPTY    -> No PLC program has been loaded yet
    status_response = requests.get(
        f"{BASE_URL}/api/status",
        headers=auth_headers,
        verify=False,
    )
    plc_status = status_response.json()

    # ── Read Runtime Logs ─────────────────────────────────────────────────────

    # Retrieve the runtime event log from the PLC core process.
    # Logs include INFO, WARNING, and ERROR messages from:
    #   - Plugin initialization (Modbus, OPC-UA, S7Comm)
    #   - PLC state transitions (INIT, RUNNING, STOPPED)
    #   - Error conditions (e.g. missing library files)
    logs_response = requests.get(
        f"{BASE_URL}/api/runtime-logs",
        headers=auth_headers,
        verify=False,
    )
    runtime_logs = logs_response.json()

    # ── Display Results ───────────────────────────────────────────────────────

    print(f"\n[Cycle {i + 1}/{READ_CYCLES}]")
    print(f"  PLC Status : {plc_status.get('status', 'UNKNOWN')}")

    # Show only the most recent 3 log entries to keep output readable
    log_entries = runtime_logs.get("runtime-logs", [])
    recent_logs = log_entries[-3:] if len(log_entries) >= 3 else log_entries

    print(f"  Recent Logs ({len(log_entries)} total, showing last {len(recent_logs)}):")
    for entry in recent_logs:
        level = entry.get("level", "INFO")
        message = entry.get("message", "")
        timestamp = entry.get("timestamp", "")
        print(f"    [{level}] {timestamp} - {message}")

    # Wait before next read cycle
    if i < READ_CYCLES - 1:
        time.sleep(READ_INTERVAL)

print("\n" + "=" * 50)
print("  Read complete.")
print("=" * 50)
