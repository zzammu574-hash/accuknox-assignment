"""
Problem Statement 1.1 — API Data Retrieval and Storage
=======================================================
Fetch a list of books from a public REST API (Open Library Search API),
store the results in a local SQLite database, and display the retrieved data.

Assumption:
    Using the Open Library Search API (https://openlibrary.org/search.json)
    as the external REST API, since it is free, public, and returns book
    data (title, author, first_publish_year) in JSON format without
    requiring an API key.
    
    Query used: subject:"python programming" — returns real-world books.

Dependencies: requests (pip install requests)
"""

import sqlite3
import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL = "https://openlibrary.org/search.json"
QUERY_PARAMS = {
    "subject": "python programming",
    "fields": "title,author_name,first_publish_year",
    "limit": 20,
}
DB_PATH = "books.db"


# ---------------------------------------------------------------------------
# Step 1: Fetch data from the REST API
# ---------------------------------------------------------------------------
def fetch_books(api_url: str, params: dict) -> list[dict]:
    """
    Call the Open Library Search API and return a normalised list of books.
    Each book is a dict with keys: title, author, publication_year.
    """
    print("Fetching books from API …")
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[ERROR] Could not reach the API: {exc}")
        return []

    raw_docs = response.json().get("docs", [])

    books = []
    for doc in raw_docs:
        title = doc.get("title", "Unknown Title")
        # author_name is a list; take the first entry if available
        authors = doc.get("author_name", [])
        author = authors[0] if authors else "Unknown Author"
        year = doc.get("first_publish_year")
        books.append({"title": title, "author": author, "publication_year": year})

    print(f"  → {len(books)} books retrieved.")
    return books


# ---------------------------------------------------------------------------
# Step 2: Store data in SQLite
# ---------------------------------------------------------------------------
def create_database(db_path: str) -> sqlite3.Connection:
    """Create (or open) the SQLite database and ensure the books table exists."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            title            TEXT    NOT NULL,
            author           TEXT,
            publication_year INTEGER
        )
    """)
    conn.commit()
    print(f"Database ready at '{db_path}'.")
    return conn


def insert_books(conn: sqlite3.Connection, books: list[dict]) -> None:
    """Insert a list of book dicts into the books table (skip duplicates by title)."""
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for book in books:
        # Avoid re-inserting the same title on repeated runs
        cursor.execute("SELECT id FROM books WHERE title = ?", (book["title"],))
        if cursor.fetchone():
            skipped += 1
            continue
        cursor.execute(
            "INSERT INTO books (title, author, publication_year) VALUES (?, ?, ?)",
            (book["title"], book["author"], book["publication_year"]),
        )
        inserted += 1
    conn.commit()
    print(f"  → {inserted} books inserted, {skipped} duplicates skipped.")


# ---------------------------------------------------------------------------
# Step 3: Display the data
# ---------------------------------------------------------------------------
def display_books(conn: sqlite3.Connection) -> None:
    """Fetch all books from the database and print them as a formatted table."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, publication_year FROM books ORDER BY publication_year")
    rows = cursor.fetchall()

    if not rows:
        print("No books found in the database.")
        return

    # Column widths
    col_widths = [4, 60, 30, 4]
    header = (
        f"{'ID':<{col_widths[0]}}  "
        f"{'Title':<{col_widths[1]}}  "
        f"{'Author':<{col_widths[2]}}  "
        f"{'Year':<{col_widths[3]}}"
    )
    separator = "-" * len(header)

    print("\n" + separator)
    print(header)
    print(separator)
    for row_id, title, author, year in rows:
        title_display  = (title[:57]  + "…") if len(title)  > 60 else title
        author_display = (author[:27] + "…") if len(author) > 30 else author
        year_display   = str(year) if year else "N/A"
        print(
            f"{row_id:<{col_widths[0]}}  "
            f"{title_display:<{col_widths[1]}}  "
            f"{author_display:<{col_widths[2]}}  "
            f"{year_display:<{col_widths[3]}}"
        )
    print(separator)
    print(f"\nTotal books in database: {len(rows)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    books = fetch_books(API_URL, QUERY_PARAMS)
    conn  = create_database(DB_PATH)
    insert_books(conn, books)
    display_books(conn)
    conn.close()


if __name__ == "__main__":
    main()
