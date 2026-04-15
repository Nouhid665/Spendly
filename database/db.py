import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "spendly.db"


def get_db():
    """Open a connection to the SQLite database with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist. Safe to call multiple times."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(name, email, password):
    """Create a new user with hashed password.

    Args:
        name: User's full name
        email: User's email address
        password: Plain text password (will be hashed)

    Returns:
        User ID on success, None if email already exists
    """
    conn = get_db()
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # Email already exists (UNIQUE constraint)
        conn.close()
        return None


def seed_db():
    """Insert sample data for development. Idempotent - won't duplicate on re-runs."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded

    # Create demo user
    demo_email = "demo@spendly.com"
    demo_password = generate_password_hash("demo123")

    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, ("Demo User", demo_email, demo_password))

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
    user_id = cursor.fetchone()[0]

    # Insert 8 sample expenses across all 7 categories
    # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
    sample_expenses = [
        (15.50, "Food", "2026-04-01", "Lunch at cafe"),
        (45.00, "Transport", "2026-04-02", "Uber ride to airport"),
        (120.00, "Bills", "2026-04-03", "Electric bill"),
        (35.00, "Health", "2026-04-05", "Pharmacy - vitamins"),
        (60.00, "Entertainment", "2026-04-07", "Movie tickets and dinner"),
        (200.00, "Shopping", "2026-04-10", "New shoes"),
        (25.00, "Other", "2026-04-12", "Gift for friend"),
        (12.75, "Food", "2026-04-14", "Coffee and pastries"),
    ]

    cursor.executemany("""
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, [(user_id, *expense) for expense in sample_expenses])

    conn.commit()
    conn.close()
