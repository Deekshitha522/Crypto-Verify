import sqlite3

conn = sqlite3.connect("certificates.db")
cursor = conn.cursor()

# -------------------------------
# Certificates table (Existing)
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS certificates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    certificate_id TEXT UNIQUE,
    student_name TEXT,
    usn TEXT,
    course TEXT,
    cgpa TEXT,
    issue_date TEXT,
    hash TEXT,
    signature TEXT,
    status TEXT
)
""")

# Add pdf_name column if it doesn't exist
cursor.execute("PRAGMA table_info(certificates)")
columns = [column[1] for column in cursor.fetchall()]

if "pdf_name" not in columns:
    cursor.execute("ALTER TABLE certificates ADD COLUMN pdf_name TEXT")

# -------------------------------
# Users table (NEW)
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    security_answer TEXT NOT NULL
)
""")

# Insert default admin only once
cursor.execute("""
INSERT OR IGNORE INTO users
(id, full_name, username, password, security_answer)
VALUES
(1, 'Administrator', 'admin', 'SJEC@2026', 'cryptoverify')
""")

conn.commit()
conn.close()

print("Database Ready!")