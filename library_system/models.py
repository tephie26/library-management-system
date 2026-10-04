from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = ""


@dataclass
class Member:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class Book:
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    isbn: str = ""
    copies_available: int = 0


@dataclass
class Loan:
    id: Optional[int] = None
    member_id: int = 0
    book_id: int = 0
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    return_date: Optional[date] = None
