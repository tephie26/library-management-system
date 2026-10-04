import sqlite3
from datetime import date, timedelta
from typing import List, Optional
from contextlib import contextmanager

from library_system.models import User, Member, Book, Loan


class LibraryRepository:
    """Data access layer for the library system."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def _connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initialize database schema."""
        with self._connection() as conn:
            cursor = conn.cursor()

            # Users table (admin and librarians)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'librarian'))
                )
            """)

            # Members table (borrowers)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL
                )
            """)

            # Books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE NOT NULL,
                    copies_available INTEGER NOT NULL CHECK(copies_available >= 0)
                )
            """)

            # Loans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    issue_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    return_date TEXT,
                    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE RESTRICT,
                    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE RESTRICT
                )
            """)

            conn.commit()

    def clear_all(self):
        """Clear all tables (for testing)."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loans")
            cursor.execute("DELETE FROM books")
            cursor.execute("DELETE FROM members")
            cursor.execute("DELETE FROM users")
            conn.commit()

    # Users
    def create_user(self, user: User) -> int:
        """Create a user. Returns the user ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                (user.username, user.hashed_password, user.role),
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, hashed_password, role FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    hashed_password=row[2],
                    role=row[3],
                )
            return None

    # Members
    def create_member(self, member: Member) -> int:
        """Create a member. Returns the member ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
                (member.name, member.email, member.phone),
            )
            conn.commit()
            return cursor.lastrowid

    def get_member(self, member_id: int) -> Optional[Member]:
        """Retrieve a member by ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, phone FROM members WHERE id = ?",
                (member_id,),
            )
            row = cursor.fetchone()
            if row:
                return Member(id=row[0], name=row[1], email=row[2], phone=row[3])
            return None

    def list_members(self) -> List[Member]:
        """List all members."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, phone FROM members ORDER BY name")
            rows = cursor.fetchall()
            return [Member(id=r[0], name=r[1], email=r[2], phone=r[3]) for r in rows]

    def update_member(self, member: Member):
        """Update a member."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?",
                (member.name, member.email, member.phone, member.id),
            )
            conn.commit()

    def delete_member(self, member_id: int):
        """Delete a member."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()

    # Books
    def create_book(self, book: Book) -> int:
        """Create a book. Returns the book ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, isbn, copies_available) VALUES (?, ?, ?, ?)",
                (book.title, book.author, book.isbn, book.copies_available),
            )
            conn.commit()
            return cursor.lastrowid

    def get_book(self, book_id: int) -> Optional[Book]:
        """Retrieve a book by ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, author, isbn, copies_available FROM books WHERE id = ?",
                (book_id,),
            )
            row = cursor.fetchone()
            if row:
                return Book(
                    id=row[0],
                    title=row[1],
                    author=row[2],
                    isbn=row[3],
                    copies_available=row[4],
                )
            return None

    def list_books(self) -> List[Book]:
        """List all books."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, author, isbn, copies_available FROM books ORDER BY title"
            )
            rows = cursor.fetchall()
            return [
                Book(
                    id=r[0],
                    title=r[1],
                    author=r[2],
                    isbn=r[3],
                    copies_available=r[4],
                )
                for r in rows
            ]

    def update_book(self, book: Book):
        """Update a book."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET title = ?, author = ?, isbn = ?, copies_available = ? WHERE id = ?",
                (book.title, book.author, book.isbn, book.copies_available, book.id),
            )
            conn.commit()

    def delete_book(self, book_id: int):
        """Delete a book."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()

    # Loans
    def create_loan(self, loan: Loan) -> int:
        """Create a loan. Returns the loan ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO loans (member_id, book_id, issue_date, due_date, return_date) VALUES (?, ?, ?, ?, ?)",
                (
                    loan.member_id,
                    loan.book_id,
                    loan.issue_date.isoformat(),
                    loan.due_date.isoformat(),
                    loan.return_date.isoformat() if loan.return_date else None,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_loan(self, loan_id: int) -> Optional[Loan]:
        """Retrieve a loan by ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, member_id, book_id, issue_date, due_date, return_date FROM loans WHERE id = ?",
                (loan_id,),
            )
            row = cursor.fetchone()
            if row:
                return Loan(
                    id=row[0],
                    member_id=row[1],
                    book_id=row[2],
                    issue_date=date.fromisoformat(row[3]),
                    due_date=date.fromisoformat(row[4]),
                    return_date=date.fromisoformat(row[5]) if row[5] else None,
                )
            return None

    def list_loans(self) -> List[Loan]:
        """List all loans."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, member_id, book_id, issue_date, due_date, return_date FROM loans ORDER BY issue_date DESC"
            )
            rows = cursor.fetchall()
            return [
                Loan(
                    id=r[0],
                    member_id=r[1],
                    book_id=r[2],
                    issue_date=date.fromisoformat(r[3]),
                    due_date=date.fromisoformat(r[4]),
                    return_date=date.fromisoformat(r[5]) if r[5] else None,
                )
                for r in rows
            ]

    def list_active_loans(self) -> List[Loan]:
        """List active loans (not returned)."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, member_id, book_id, issue_date, due_date, return_date FROM loans WHERE return_date IS NULL ORDER BY issue_date DESC"
            )
            rows = cursor.fetchall()
            return [
                Loan(
                    id=r[0],
                    member_id=r[1],
                    book_id=r[2],
                    issue_date=date.fromisoformat(r[3]),
                    due_date=date.fromisoformat(r[4]),
                    return_date=date.fromisoformat(r[5]) if r[5] else None,
                )
                for r in rows
            ]

    def update_loan(self, loan: Loan):
        """Update a loan (e.g., mark as returned)."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE loans SET return_date = ? WHERE id = ?",
                (loan.return_date.isoformat() if loan.return_date else None, loan.id),
            )
            conn.commit()

    def get_active_loan(self, member_id: int, book_id: int) -> Optional[Loan]:
        """Get an active loan for a member and book."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, member_id, book_id, issue_date, due_date, return_date FROM loans WHERE member_id = ? AND book_id = ? AND return_date IS NULL",
                (member_id, book_id),
            )
            row = cursor.fetchone()
            if row:
                return Loan(
                    id=row[0],
                    member_id=row[1],
                    book_id=row[2],
                    issue_date=date.fromisoformat(row[3]),
                    due_date=date.fromisoformat(row[4]),
                    return_date=date.fromisoformat(row[5]) if row[5] else None,
                )
            return None

    def increment_copies(self, book_id: int):
        """Increment available copies of a book."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET copies_available = copies_available + 1 WHERE id = ?",
                (book_id,),
            )
            conn.commit()

    def decrement_copies(self, book_id: int):
        """Decrement available copies of a book."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE books SET copies_available = copies_available - 1 WHERE id = ?",
                (book_id,),
            )
            conn.commit()
