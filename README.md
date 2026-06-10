# Securing PLC-to-AI Data Pipelines with PKI

A practical industrial cybersecurity project that demonstrates how to secure the data pipeline between an industrial PLC (Programmable Logic Controller) and an AI analytics server, using Public Key Infrastructure (PKI) and TLS 1.3.

The project builds two versions of the same pipeline — an **insecure** one and a **secure** one — and compares them, showing exactly how much sensitive operational data is exposed when industrial traffic is left unencrypted, and how TLS 1.3 with an X.509 certificate closes that gap.

Built for the **Internet Security** module at the **University of Northampton**.

> **Security note:** This is an educational lab project. The private keys and certificates used during testing are intentionally **not** included in this repository — they should always be generated locally with `generate_cert.py` and never committed to version control.

---

## The Problem

Industrial control systems increasingly connect Operational Technology (OT) — PLCs controlling physical processes — to IT and AI platforms over standard IP networks. Many industrial protocols were designed decades ago with no encryption, so sensitive data such as temperature readings, alarm states and system status often travels in plain text. This leaves it exposed to anyone able to observe the network, which has contributed to real-world safety and security incidents in industrial environments.

## What This Project Does

It implements a PLC-to-AI pipeline with three components:

- **OpenPLC Runtime v4** — acts as the industrial PLC, running a Structured Text program that simulates a temperature-monitoring system with heater control and alarm logic.
- **A Python bridge** — authenticates to OpenPLC, reads sensor values every two seconds, and forwards them as JSON to the analytics server.
- **A Flask server** — represents the AI analytics endpoint that receives the data.

Two scenarios are then compared:

| | Insecure | Secure |
|---|---|---|
| Protocol | HTTP | HTTPS |
| Encryption | None (plain text) | TLS 1.3 |
| Certificate | None | Self-signed X.509, RSA 4096-bit |
| Wireshark capture | Fully readable | Encrypted / unreadable |

The result confirms that enabling TLS 1.3 provides confidentiality, integrity and authentication at once, making intercepted traffic unreadable without the private key.

## Tech Stack

- **Python** (Flask) — analytics server and bridge scripts
- **OpenPLC Runtime v4** — PLC simulator
- **TLS 1.3 / PKI** — X.509 certificates, RSA 4096-bit, OpenSSL
- **Structured Text (IEC 61131-3)** — PLC control logic
- **Wireshark** — traffic analysis and verification

## Running It

First, generate the certificate and key locally (this creates `cert.pem` and `key.pem`, which stay on your machine):

```bash
cd secure
python generate_cert.py
```

Then run the secure server and bridge:

```bash
python flask_server_secure.py     # HTTPS server
python plc_bridge_secure.py       # reads PLC data and forwards it over TLS
```

The `insecure/` scripts run the same pipeline over plain HTTP for comparison, and `standalone/` contains a simplified version that demonstrates the same secure-vs-insecure concept without needing OpenPLC.

## Key Findings

- Unencrypted industrial traffic exposes all operational data to anyone on the network.
- Upgrading to TLS 1.3 requires very little code change but fully protects data in transit.
- Findings were mapped to **ISO 27001 / 27002** security controls, with recommendations covering certificate management, mutual TLS, and network monitoring.
