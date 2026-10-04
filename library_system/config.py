import os

DATABASE_PATH = os.getenv("LIBRARY_DB_PATH", "library.db")

DEMO_USERS = [
    ("admin", "admin123", "admin"),
    ("librarian", "lib123", "librarian"),
]

DEMO_MEMBERS = [
    ("Alice Johnson", "alice@example.com", "555-1001"),
    ("Bob Smith", "bob@example.com", "555-1002"),
    ("Carol White", "carol@example.com", "555-1003"),
]

DEMO_BOOKS = [
    ("Python Crash Course", "Eric Matthes", "9781593279288", 3),
    ("Clean Code", "Robert C. Martin", "9780132350884", 2),
    ("The Pragmatic Programmer", "Andrew Hunt", "9780201616224", 4),
    ("Deep Work", "Cal Newport", "9781455586691", 2),
]
