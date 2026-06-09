"""
start_plc.py
------------
This script monitors the PLC program compilation status on the OpenPLC
Runtime and then starts the PLC execution once compilation is complete.

Workflow:
    1. Authenticate with the OpenPLC Runtime API
    2. Poll the compilation status until it reaches a final state
       (SUCCESS, FAILED, or STOPPED)
    3. If compilation succeeded, send the start command to the PLC
    4. Verify the PLC is now in RUNNING state

This script is typically run after fix_and_upload.py has uploaded
and triggered compilation of the PLC program.

Compilation states:
    IDLE        -> No compilation has been triggered yet
    UNZIPPING   -> ZIP archive is being extracted
    COMPILING   -> GCC is compiling the C source files
    SUCCESS     -> Compilation finished successfully
    FAILED      -> Compilation encountered an error (check logs)
    STOPPED     -> PLC was stopped during/after compilation
"""

import time

import requests
import urllib3

# Suppress SSL warnings from the self-signed certificate on OpenPLC Runtime
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime HTTPS API endpoint
BASE_URL = "https://127.0.0.1:8443"

# Maximum number of status polling attempts before giving up
MAX_POLL_ATTEMPTS = 10

# Delay between each polling attempt (seconds)
POLL_INTERVAL = 3

# Final states that indicate compilation has finished (success or failure)
FINAL_STATES = {"SUCCESS", "FAILED", "STOPPED"}

# ─── Authentication ───────────────────────────────────────────────────────────

# Login to OpenPLC Runtime and retrieve a JWT access token
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,  # Accept self-signed TLS certificate
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("=" * 50)
print("  OpenPLC Runtime - Compilation Monitor")
print("=" * 50)

# ─── Poll Compilation Status ──────────────────────────────────────────────────

compilation_succeeded = False

for i in range(MAX_POLL_ATTEMPTS):

    # Request current compilation status from the Runtime
    comp_response = requests.get(
        f"{BASE_URL}/api/compilation-status",
        headers=auth_headers,
        verify=False,
    )
    comp_data = comp_response.json()
    current_status = comp_data.get("status", "UNKNOWN")

    print(f"[{i + 1}/{MAX_POLL_ATTEMPTS}] Compilation status: {current_status}")

    # Check if compilation has reached a final state
    if current_status in FINAL_STATES:

        if current_status == "FAILED":
            # Print the last 10 log lines to help diagnose the build error
            print("\n[ERROR] Compilation failed. Last 10 log lines:")
            logs = comp_data.get("logs", [])
            for log_line in logs[-10:]:
                print(f"  {log_line}")

        elif current_status == "SUCCESS":
            print("\n[OK] Compilation succeeded!")
            compilation_succeeded = True

        elif current_status == "STOPPED":
            # STOPPED after a successful compile means the Runtime
            # auto-reloaded the PLC program and is ready to start
            print("\n[OK] Compilation finished and PLC is ready to start.")
            compilation_succeeded = True

        break

    # Not finished yet — wait before polling again
    time.sleep(POLL_INTERVAL)

else:
    # Loop completed without hitting a final state
    print(
        f"\n[WARNING] Compilation did not finish within "
        f"{MAX_POLL_ATTEMPTS * POLL_INTERVAL} seconds."
    )

# ─── Start PLC ────────────────────────────────────────────────────────────────

print("\n" + "=" * 50)
print("  Sending START command to PLC...")
print("=" * 50)

# Send the start command to begin PLC scan cycle execution.
# Note: This is a GET request (not POST) as defined by the OpenPLC Runtime API.
# Possible responses:
#   START:OK                -> PLC started successfully
#   START:ERROR             -> Failed to start (e.g. no program loaded)
#   START:ERROR_ALREADY_RUNNING -> PLC was already running (not an error)
start_response = requests.get(
    f"{BASE_URL}/api/start-plc",
    headers=auth_headers,
    verify=False,
)
start_result = start_response.json()
print(f"Start command response: {start_result}")

# ─── Verify PLC is Running ────────────────────────────────────────────────────

# Wait briefly for the PLC to transition to RUNNING state
time.sleep(2)

# Query the final PLC status to confirm it is running
status_response = requests.get(
    f"{BASE_URL}/api/status",
    headers=auth_headers,
    verify=False,
)
final_status = status_response.json().get("status", "UNKNOWN")

print(f"\nFinal PLC Status: {final_status}")

if final_status == "STATUS:RUNNING":
    print("✅ PLC is now RUNNING successfully!")
else:
    print(f"⚠️  Unexpected PLC status: {final_status}")
