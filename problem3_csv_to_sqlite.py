"""
Problem Statement 1.3 — CSV Data Import to a Database
======================================================
Read user information from a CSV file (name, email, age, city, signup_date)
and insert the records into a SQLite database with full validation,
duplicate detection, and a summary report.

Assumptions:
    • The CSV file is 'sample_users.csv' located in the same directory.
      A different path can be supplied via the command line:
          python problem3_csv_to_sqlite.py path/to/users.csv
    • Email is treated as the natural unique key — re-running the script
      will skip rows whose email already exists rather than raising an error.
    • Rows with missing name or email, or with a malformed email address,
      are logged as validation errors and skipped.
    • The SQLite database file is 'users.db'.

No third-party libraries required — only the Python standard library.
"""

import csv
import sqlite3
import re
import sys
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_CSV_PATH = "sample_users.csv"
DB_PATH          = "users.db"

# Basic email pattern: something@something.something
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def validate_row(row: dict, line_number: int) -> tuple[bool, str]:
    """
    Validate a single CSV row.
    Returns (is_valid: bool, reason: str).
    """
    name  = row.get("name", "").strip()
    email = row.get("email", "").strip()

    if not name:
        return False, f"Line {line_number}: missing 'name' field."
    if not email:
        return False, f"Line {line_number}: missing 'email' field."
    if not EMAIL_RE.match(email):
        return False, f"Line {line_number}: invalid email '{email}'."

    # Optional: validate signup_date format if present
    signup_date = row.get("signup_date", "").strip()
    if signup_date:
        try:
            datetime.strptime(signup_date, "%Y-%m-%d")
        except ValueError:
            return False, (
                f"Line {line_number}: 'signup_date' '{signup_date}' "
                f"is not in YYYY-MM-DD format."
            )

    return True, ""


def normalise_row(row: dict) -> dict:
    """Strip whitespace from all string fields and normalise email to lower-case."""
    return {
        "name":        row.get("name", "").strip(),
        "email":       row.get("email", "").strip().lower(),
        "age":         int(row["age"]) if row.get("age", "").strip().isdigit() else None,
        "city":        row.get("city", "").strip() or None,
        "signup_date": row.get("signup_date", "").strip() or None,
    }


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def create_database(db_path: str) -> sqlite3.Connection:
    """Open / create the SQLite database and ensure the users table exists."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")   # safer concurrent writes
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            age         INTEGER,
            city        TEXT,
            signup_date TEXT,
            imported_at TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    print(f"Database ready: '{db_path}'")
    return conn


def insert_user(conn: sqlite3.Connection, user: dict) -> str:
    """
    Insert one user record.
    Returns 'inserted', 'duplicate', or 'error:<message>'.
    """
    try:
        conn.execute(
            """
            INSERT INTO users (name, email, age, city, signup_date)
            VALUES (:name, :email, :age, :city, :signup_date)
            """,
            user,
        )
        conn.commit()
        return "inserted"
    except sqlite3.IntegrityError:
        # UNIQUE constraint on email
        return "duplicate"
    except sqlite3.Error as exc:
        return f"error:{exc}"


# ---------------------------------------------------------------------------
# CSV import
# ---------------------------------------------------------------------------
def import_csv(csv_path: str, conn: sqlite3.Connection) -> None:
    """
    Read the CSV file row by row, validate each row, insert valid rows,
    and print a detailed summary at the end.
    """
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: '{csv_path}'")
        sys.exit(1)

    counters = {"inserted": 0, "duplicate": 0, "invalid": 0, "error": 0}
    errors:    list[str] = []

    print(f"\nImporting from '{csv_path}' …\n")

    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)

        # Check required columns exist
        required_cols = {"name", "email"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            print(f"[ERROR] CSV is missing required columns: {missing}")
            sys.exit(1)

        for line_number, raw_row in enumerate(reader, start=2):  # start=2: header is line 1
            # --- Validate ---
            valid, reason = validate_row(raw_row, line_number)
            if not valid:
                counters["invalid"] += 1
                errors.append(reason)
                continue

            # --- Normalise ---
            user = normalise_row(raw_row)

            # --- Insert ---
            result = insert_user(conn, user)
            if result == "inserted":
                counters["inserted"] += 1
                print(f"  [OK]  {user['name']:<22}  {user['email']}")
            elif result == "duplicate":
                counters["duplicate"] += 1
                print(f"  [SKIP] Duplicate email: {user['email']}")
            else:
                counters["error"] += 1
                errors.append(f"Line {line_number}: DB error — {result.split(':', 1)[1]}")

    # --- Summary ---
    total = sum(counters.values())
    print("\n" + "=" * 55)
    print("  IMPORT SUMMARY")
    print("=" * 55)
    print(f"  Total rows processed : {total}")
    print(f"  Inserted             : {counters['inserted']}")
    print(f"  Skipped (duplicate)  : {counters['duplicate']}")
    print(f"  Skipped (invalid)    : {counters['invalid']}")
    print(f"  Errors               : {counters['error']}")
    if errors:
        print("\n  Issues encountered:")
        for err in errors:
            print(f"    • {err}")
    print("=" * 55)


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display_users(conn: sqlite3.Connection) -> None:
    """Pretty-print every user currently stored in the database."""
    cursor = conn.execute(
        "SELECT id, name, email, age, city, signup_date FROM users ORDER BY id"
    )
    rows = cursor.fetchall()

    if not rows:
        print("\nNo users found in the database.")
        return

    col = [4, 22, 34, 4, 16, 12]
    header = (
        f"{'ID':<{col[0]}}  {'Name':<{col[1]}}  {'Email':<{col[2]}}  "
        f"{'Age':<{col[3]}}  {'City':<{col[4]}}  {'Signup':<{col[5]}}"
    )
    sep = "─" * len(header)

    print(f"\n{sep}")
    print(header)
    print(sep)
    for uid, name, email, age, city, signup in rows:
        print(
            f"{uid:<{col[0]}}  {name:<{col[1]}}  {email:<{col[2]}}  "
            f"{str(age) if age else 'N/A':<{col[3]}}  "
            f"{(city or 'N/A'):<{col[4]}}  "
            f"{(signup or 'N/A'):<{col[5]}}"
        )
    print(sep)
    print(f"\nTotal users in database: {len(rows)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    conn = create_database(DB_PATH)
    import_csv(csv_path, conn)
    display_users(conn)
    conn.close()


if __name__ == "__main__":
    main()
