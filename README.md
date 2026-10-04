# Library Management System

A simple menu-driven library system built with Python, SQLite, bcrypt, pandas, and matplotlib.

Features:
- Login for admin and librarian users
- Hash passwords with bcrypt
- CRUD for books
- CRUD for members
- Issue and return books with stock checks and transactional updates
- Search books by title or author
- Bulk import from CSV
- Summary report with a chart

Project structure:
- `library_system/` — app package
- `main.py` — app entry point
- `tests/` — automated tests

Quick start:

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python main.py
   ```

3. Demo credentials:
   - admin / admin123
   - librarian / lib123

4. Run tests:
   ```bash
   python -m unittest discover -s tests -v
   ```

Database schema:
- users(id, username, password_hash, role)
- members(id, name, email, phone)
- books(id, title, author, isbn, copies_available)
- loans(id, member_id, book_id, issue_date, due_date, return_date)

Notes:
- All inventory updates during issue/return are done in a database transaction.
- Search supports case-insensitive partial matches.
- CSV import expects columns: title, author, isbn, copies.
