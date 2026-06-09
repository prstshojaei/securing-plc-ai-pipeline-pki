"""
flask_server.py
---------------
This is the INSECURE version of the Flask data receiver server.

It listens on HTTP (port 5000) WITHOUT any encryption or TLS.
This means all PLC data transmitted to this server is sent as plain text
and can be intercepted and read by anyone on the network using tools
like Wireshark.

Purpose in this project:
    Demonstrate the security vulnerability of unencrypted industrial
    data pipelines. This server represents the "before security" scenario.

Endpoints:
    POST /plc-data  - Receive PLC sensor data from the bridge script
    GET  /data      - View all received data records
"""

import datetime

from flask import Flask, jsonify, request

# ─── Application Setup ────────────────────────────────────────────────────────

app = Flask(__name__)

# In-memory storage for all received PLC data records
# In a real system this would be a database
received_data = []

# ─── Routes ───────────────────────────────────────────────────────────────────


@app.route("/plc-data", methods=["POST"])
def receive_data():
    """
    Receive PLC sensor data sent by the bridge script (plc_bridge.py).

    Expected JSON payload:
        {
            "cycle":          int   - cycle counter from the bridge
            "plc_status":     str   - e.g. "STATUS:RUNNING"
            "temperature":    int   - simulated temperature in Celsius
            "heater_on":      bool  - whether the heater is active
            "alarm_high":     bool  - True if temperature >= high_limit
            "alarm_critical": bool  - True if temperature >= critical_limit
            "system_ok":      bool  - overall system health
        }

    SECURITY NOTE:
        This endpoint uses plain HTTP. The JSON payload is transmitted
        without encryption and is fully visible in Wireshark or any
        network sniffer on the same network segment.
    """
    # Parse the incoming JSON body
    data = request.get_json()

    # Attach a server-side timestamp to the record
    data["timestamp"] = str(datetime.datetime.now())

    # Store the record in memory
    received_data.append(data)

    # Print a human-readable summary to the console
    print(f"\n[INSECURE - HTTP] Received PLC Data:")
    print(f"   Timestamp   : {data['timestamp']}")
    print(f"   Temperature : {data.get('temperature')} C")
    print(f"   Heater ON   : {data.get('heater_on')}")
    print(f"   Alarm High  : {data.get('alarm_high')}")
    print(f"   System OK   : {data.get('system_ok')}")
    print(f"   PLC Status  : {data.get('plc_status')}")

    # Return acknowledgement to the sender
    return jsonify(
        {
            "status": "received",
            "timestamp": data["timestamp"],
            "warning": "DATA TRANSMITTED OVER UNENCRYPTED HTTP - NOT SECURE",
        }
    )


@app.route("/data", methods=["GET"])
def show_data():
    """
    Return all PLC data records received so far.

    Useful for verifying that data is arriving correctly
    and for demonstrating the full data captured during the demo.
    """
    return jsonify({"total_records": len(received_data), "records": received_data})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Flask PLC Data Receiver - INSECURE (HTTP) MODE")
    print("=" * 55)
    print("  Protocol : HTTP (no encryption)")
    print("  Port     : 5000")
    print("  WARNING  : All data is transmitted as plain text!")
    print("  Endpoint : http://127.0.0.1:5000/plc-data")
    print("=" * 55)

    # Run on all network interfaces so it can receive from the bridge script.
    # debug=False is important for any demo/production-like environment.
    app.run(host="0.0.0.0", port=5000, debug=False)
