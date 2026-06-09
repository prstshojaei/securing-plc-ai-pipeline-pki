"""
generate_cert.py
----------------
Generates a self-signed TLS certificate and private key
using OpenSSL for the secure Flask server.

This is the PKI foundation of the secure scenario:
- RSA 4096-bit private key
- Self-signed X.509 certificate
- Valid for localhost and 127.0.0.1
"""

import os
import subprocess

# Save certificate files in the same directory as this script
CERT_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(CERT_DIR, "cert.pem")
KEY_FILE = os.path.join(CERT_DIR, "key.pem")

print("=" * 55)
print("  PKI Certificate Generator")
print("  Generating Self-Signed X.509 TLS Certificate")
print("=" * 55)

cmd = [
    "openssl",
    "req",
    "-x509",
    "-newkey",
    "rsa:4096",
    "-sha256",
    "-nodes",
    "-keyout",
    KEY_FILE,
    "-out",
    CERT_FILE,
    "-days",
    "365",
    "-subj",
    "/CN=localhost/O=PLC Security Project/C=GB",
    "-addext",
    "subjectAltName=DNS:localhost,IP:127.0.0.1",
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Certificate generated successfully!")
    print(f"   Algorithm   : RSA 4096-bit")
    print(f"   Hash        : SHA-256")
    print(f"   Validity    : 365 days")
    print(f"   Certificate : {CERT_FILE}")
    print(f"   Private Key : {KEY_FILE}")
    print("=" * 55)
else:
    print(f"❌ Error generating certificate:")
    print(result.stderr)
