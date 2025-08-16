import mysql.connector

conn = mysql.connector.connect(
    host="local",
    user="user",
    password="yourpass",
    database="db"  # same as .env DB_DATABASE
)
cursor = conn.cursor()

# Example insert
cursor.execute("""
    INSERT INTO events (title, source_url, date, location, description, organizer)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (
    "Test Event",
    "https://example.com",
    "2025-08-01",
    "Hyderabad",
    "Description here",
    "Organizer Name"
))

conn.commit()
conn.close()
