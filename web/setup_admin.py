"""
setup_admin.py — Interactive setup script for the Flask admin account.
Prompts for a password, hashes it with SHA-256, generates a SECRET_KEY,
and writes both to a .env file.  Run once before starting the server.
"""

import getpass
import hashlib
import os
import secrets
import sys

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def sha256_hex(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def main() -> None:
    print("=== Cotiviti IT Ticket Triage — Admin Setup ===\n")

    # Check for existing .env
    if os.path.exists(ENV_FILE):
        answer = input(".env already exists. Overwrite it? [y/N] ").strip().lower()
        if answer != "y":
            print("Setup cancelled. Existing .env unchanged.")
            sys.exit(0)

    # Collect password
    while True:
        password = getpass.getpass("Enter admin password (min 8 characters): ")
        if len(password) < 8:
            print("Password must be at least 8 characters. Try again.\n")
            continue
        confirm = getpass.getpass("Confirm admin password: ")
        if password != confirm:
            print("Passwords do not match. Try again.\n")
            continue
        break

    password_hash = sha256_hex(password)
    secret_key = secrets.token_hex(32)

    env_content = (
        f"ADMIN_PASSWORD_HASH={password_hash}\n"
        f"SECRET_KEY={secret_key}\n"
    )

    with open(ENV_FILE, "w", encoding="utf-8") as fh:
        fh.write(env_content)

    print("\n.env written successfully.")
    print("Keep this file secret — it is listed in .gitignore.")
    print("You can now start the server with:  flask --app app run")


if __name__ == "__main__":
    main()
