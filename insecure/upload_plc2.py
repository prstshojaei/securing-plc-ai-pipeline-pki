"""
upload_plc2.py
--------------
This is an earlier version of the PLC upload script.
It was written before the root cause of the linker error was fully understood.

Problem this version tried to solve:
    The linker was failing with:
        "undefined reference to MAIN_init__"
        "undefined reference to MAIN_body__"

    These functions are defined in POUS.inc. The theory at this stage
    was that adding POUS.inc as a separate POUS.c file would fix the issue.

Why this version did NOT fully work:
    Adding POUS.inc as POUS.c caused a duplicate symbol error because
    Res0.c was already including POUS.h (the header), and the build script
    was not set up to compile a standalone POUS.c file.

What the final fix was:
    Appending #include "POUS.inc" directly inside Res0.c so that
    MAIN_init__ and MAIN_body__ are compiled as part of Res0.c itself.
    This is implemented in fix_and_upload.py (the final version).

Note:
    This file is kept for reference to document the troubleshooting process.
    Use fix_and_upload.py for the working upload procedure.
"""

import os
import zipfile

import requests
import urllib3

# Suppress SSL warnings from the self-signed certificate on OpenPLC Runtime
urllib3.disable_warnings()

# ─── Configuration ────────────────────────────────────────────────────────────

# OpenPLC Runtime HTTPS API endpoint
BASE_URL = "https://127.0.0.1:8443"

# Directory containing the generated C source files from OpenPLC Editor
SRC_DIR = r"E:\Parastoo\STU\Uni\Msc\2\Internet Security\Project\with OPENPLC - C\PLC\build\OpenPLC Simulator\src"

# Output ZIP archive path
ZIP_PATH = r"E:\Parastoo\STU\Uni\Msc\2\Internet Security\Project\with OPENPLC - C\PLC\plc_src.zip"

# Empty C++ stub file path
EMPTY_CPP_PATH = r"E:\Parastoo\STU\Uni\Msc\2\Internet Security\Project\with OPENPLC - C\PLC\c_blocks_code.cpp"

# ─── Step 1: Create empty c_blocks_code.cpp stub ─────────────────────────────

# The build script always tries to compile c_blocks_code.cpp.
# We create an empty stub so the build does not fail on a missing file.
with open(EMPTY_CPP_PATH, "w") as f:
    f.write("// Empty stub - no custom C function blocks used\n")

print("[1/3] Empty c_blocks_code.cpp stub created.")

# ─── Step 2: Build the ZIP archive ───────────────────────────────────────────

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:

    # Add all files and subdirectories from the source directory
    for item in os.listdir(SRC_DIR):
        item_path = os.path.join(SRC_DIR, item)

        if os.path.isfile(item_path):
            # Add regular files directly to the ZIP root
            zf.write(item_path, item)

        elif os.path.isdir(item_path):
            # Add subdirectory contents (e.g. lib/ folder with IEC headers)
            for f2 in os.listdir(item_path):
                zf.write(os.path.join(item_path, f2), os.path.join(item, f2))

    # Add the empty C++ stub
    zf.write(EMPTY_CPP_PATH, "c_blocks_code.cpp")

    # Attempted fix: add POUS.inc as a separate POUS.c file so the linker
    # can find MAIN_init__ and MAIN_body__.
    # NOTE: This approach did not fully resolve the linker error.
    #       See fix_and_upload.py for the working solution.
    zf.write(os.path.join(SRC_DIR, "POUS.inc"), "POUS.c")

print(f"[2/3] ZIP archive created: {ZIP_PATH}")

# ─── Step 3: Upload to OpenPLC Runtime ───────────────────────────────────────

# Authenticate with the OpenPLC Runtime REST API
login_response = requests.post(
    f"{BASE_URL}/api/login",
    json={"username": "admin", "password": "admin123"},
    verify=False,  # Accept self-signed TLS certificate
)
token = login_response.json().get("access_token")
auth_headers = {"Authorization": f"Bearer {token}"}

print("[3/3] Authenticated. Uploading ZIP to OpenPLC Runtime...")

# Upload the ZIP file for compilation
with open(ZIP_PATH, "rb") as f:
    upload_response = requests.post(
        f"{BASE_URL}/api/upload-file",
        headers=auth_headers,
        files={"file": ("plc_src.zip", f, "application/zip")},
        verify=False,
    )

result = upload_response.json()
print(f"Upload result: {result}")

if result.get("UploadFileFail") == "":
    print("✅ Upload accepted. Compilation started.")
    print("   Run start_plc.py to monitor compilation and start the PLC.")
else:
    print(f"❌ Upload failed: {result.get('UploadFileFail')}")
