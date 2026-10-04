from datetime import date, timedelta
from typing import List, Optional
import csv
import bcrypt

from library_system.models import User, Member, Book, Loan
from library_system.repository import LibraryRepository


class LibraryService:
    """Business logic layer for the library system."""

    def __init__(self, repo: LibraryRepository):
        self.repo = repo

    # Authentication
    def register_user(self, username: str, password: str, role: str) -> User:
        """Register a new user."""
        if role not in ("admin", "librarian"):
            raise ValueError("Role must be 'admin' or 'librarian'")

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user = User(username=username, hashed_password=hashed_password, role=role)
        user.id = self.repo.create_user(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user. Returns User if successful, None otherwise."""
        user = self.repo.get_user_by_username(username)
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user.hashed_password.encode("utf-8")
        ):
            return user
        return None

    # Members
    def add_member(self, name: str, email: str, phone: str) -> Member:
        """Add a new member."""
        member = Member(name=name, email=email, phone=phone)
        member.id = self.repo.create_member(member)
        return member

    def get_member(self, member_id: int) -> Optional[Member]:
        """Get a member by ID."""
        return self.repo.get_member(member_id)

    def list_members(self) -> List[Member]:
        """List all members."""
        return self.repo.list_members()

    def update_member(self, member_id: int, name: str, email: str, phone: str) -> Member:
        """Update a member."""
        member = Member(id=member_id, name=name, email=email, phone=phone)
        self.repo.update_member(member)
        return member

    def delete_member(self, member_id: int):
        """Delete a member."""
        self.repo.delete_member(member_id)

    # Books
    def add_book(self, title: str, author: str, isbn: str, copies: int) -> Book:
        """Add a new book."""
        if copies < 1:
            raise ValueError("Must have at least 1 copy")
        book = Book(title=title, author=author, isbn=isbn, copies_available=copies)
        book.id = self.repo.create_book(book)
        return book

    def get_book(self, book_id: int) -> Optional[Book]:
        """Get a book by ID."""
        return self.repo.get_book(book_id)

    def list_books(self) -> List[Book]:
        """List all books."""
        return self.repo.list_books()

    def update_book(
        self, book_id: int, title: str, author: str, isbn: str, copies: int
    ) -> Book:
        """Update a book."""
        if copies < 0:
            raise ValueError("Copies cannot be negative")
        book = Book(id=book_id, title=title, author=author, isbn=isbn, copies_available=copies)
        self.repo.update_book(book)
        return book

    def delete_book(self, book_id: int):
        """Delete a book."""
        self.repo.delete_book(book_id)

    def search_books_by_title(self, title: str) -> List[Book]:
        """Search books by title (case-insensitive substring match)."""
        return [
            b for b in self.repo.list_books()
            if title.lower() in b.title.lower()
        ]

    def search_books_by_author(self, author: str) -> List[Book]:
        """Search books by author (case-insensitive substring match)."""
        return [
            b for b in self.repo.list_books()
            if author.lower() in b.author.lower()
        ]

    # Loans
    def issue_book(
        self, member_id: int, book_id: int, days_until_due: int = 14
    ) -> Loan:
        """Issue a book to a member. All in one atomic transaction."""
        member = self.repo.get_member(member_id)
        if not member:
            raise ValueError(f"Member {member_id} not found")

        book = self.repo.get_book(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")

        if book.copies_available <= 0:
            raise ValueError(f"Book '{book.title}' has no available copies")

        # Create loan
        issue_date = date.today()
        due_date = issue_date + timedelta(days=days_until_due)
        loan = Loan(
            member_id=member_id,
            book_id=book_id,
            issue_date=issue_date,
            due_date=due_date,
        )
        loan.id = self.repo.create_loan(loan)

        # Decrement copies
        self.repo.decrement_copies(book_id)

        return loan

    def return_book(self, loan_id: int) -> Loan:
        """Return a book (mark loan as returned)."""
        loan = self.repo.get_loan(loan_id)
        if not loan:
            raise ValueError(f"Loan {loan_id} not found")
        if loan.return_date:
            raise ValueError(f"Loan {loan_id} already returned")

        # Mark as returned
        loan.return_date = date.today()
        self.repo.update_loan(loan)

        # Increment copies
        self.repo.increment_copies(loan.book_id)

        return loan

    def list_loans(self) -> List[Loan]:
        """List all loans."""
        return self.repo.list_loans()

    def list_active_loans(self) -> List[Loan]:
        """List active (unreturned) loans."""
        return self.repo.list_active_loans()

    # Bulk import
    def bulk_import_books(self, csv_path: str) -> int:
        """Import books from a CSV file (title, author, isbn, copies).
        Returns the number of books imported.
        """
        count = 0
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        self.add_book(
                            title=row["title"],
                            author=row["author"],
                            isbn=row["isbn"],
                            copies=int(row["copies"]),
                        )
                        count += 1
                    except (KeyError, ValueError) as e:
                        print(f"Skipping row: {e}")
        except FileNotFoundError:
            raise ValueError(f"File '{csv_path}' not found")
        return count
