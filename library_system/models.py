from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    """Admin and Librarian users."""
    id: Optional[int] = None
    username: str = ""
    hashed_password: str = ""
    role: str = ""  # 'admin' or 'librarian'


@dataclass
class Member:
    """Library members who can borrow books."""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class Book:
    """Books in the library."""
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    isbn: str = ""
    copies_available: int = 0


@dataclass
class Loan:
    """Book loans (issues and returns)."""
    id: Optional[int] = None
    member_id: int = 0
    book_id: int = 0
    issue_date: date = None
    due_date: date = None
    return_date: Optional[date] = None
