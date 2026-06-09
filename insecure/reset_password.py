"""
reset_password.py
-----------------
This script resets the OpenPLC Runtime admin password directly in the
SQLite database.

Why this was needed:
    The OpenPLC Runtime stores user passwords as hashed values in a
    SQLite database. The default admin password was unknown (it had been
    changed or auto-generated). Since we could not log in via the API,
    we reset the password directly in the database.

How OpenPLC Runtime hashes passwords:
    The Runtime uses werkzeug's generate_password_hash() with a PEPPER
    value appended to the password before hashing. The PEPPER is stored
    in the .env file at:
        D:\\App\\OpenPLC Runtime\\msys64\\run\\runtime\\.env

    So the actual value hashed is: password + PEPPER

Database location (Windows/MSYS2):
    D:\\App\\OpenPLC Runtime\\msys64\\run\\runtime\\restapi.db
    Table: users
    Columns: id, username, password_hash, role

IMPORTANT:
    This script should only be used in a development/lab environment.
    In a real production system, direct database modification is a
    serious security risk and should never be done.
"""

import sqlite3

from werkzeug.security import generate_password_hash

# ─── Configuration ────────────────────────────────────────────────────────────

# The new password to set for the admin account
NEW_PASSWORD = "admin123"

# The PEPPER value from the OpenPLC Runtime .env file.
# This is appended to the password before hashing, as required by the Runtime.
# Found at: D:\App\OpenPLC Runtime\msys64\run\runtime\.env
PEPPER = "e8562a6d03eed7278baf61ee4ded819ff5e7f98841986d120922ffa8d7f46f8f"

# Path to the OpenPLC Runtime SQLite database (Windows/MSYS2 path)
DB_PATH = r"D:\App\OpenPLC Runtime\msys64\run\runtime\restapi.db"

# The username whose password will be reset
TARGET_USERNAME = "admin"

# ─── Generate New Password Hash ───────────────────────────────────────────────

# The Runtime always appends the PEPPER to the password before hashing.
# We must do the same here, otherwise the login check will fail.
# Format: hash(password + pepper)
password_with_pepper = NEW_PASSWORD + PEPPER
new_hash = generate_password_hash(password_with_pepper)

print(f"[1/3] New password hash generated.")
print(f"      Password : {NEW_PASSWORD}")
print(f"      Hash     : {new_hash[:60]}...")

# ─── Update Database ──────────────────────────────────────────────────────────

# Connect to the OpenPLC Runtime SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Update the password_hash field for the target user
cursor.execute(
    "UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, TARGET_USERNAME)
)

# Check that the update actually affected a row
if cursor.rowcount == 0:
    print(f"[ERROR] User '{TARGET_USERNAME}' not found in database.")
else:
    conn.commit()
    print(f"[2/3] Database updated successfully.")
    print(f"      User     : {TARGET_USERNAME}")
    print(f"      Database : {DB_PATH}")

conn.close()

print(f"[3/3] Done.")
print(f"\n✅ Password reset complete.")
print(f"   You can now log in with:")
print(f"   Username : {TARGET_USERNAME}")
print(f"   Password : {NEW_PASSWORD}")
