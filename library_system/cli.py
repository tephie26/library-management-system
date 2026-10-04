from datetime import date
from library_system.repository import LibraryRepository
from library_system.service import LibraryService
from library_system.config import DATABASE_PATH, DEMO_DATA


class LibraryCLI:
    """Command-line interface for the library system."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.repo = LibraryRepository(db_path)
        self.service = LibraryService(self.repo)
        self.current_user = None

    def run(self):
        """Start the CLI."""
        self.repo.init_db()
        self._seed_demo_data_if_needed()

        while True:
            if not self.current_user:
                self._login_menu()
            else:
                if self.current_user.role == "admin":
                    self._admin_menu()
                else:
                    self._librarian_menu()

    def _seed_demo_data_if_needed(self):
        """Seed demo data if tables are empty."""
        if len(self.repo.list_books()) > 0:
            return

        print("Seeding demo data...")
        # Users
        for username, password, role in DEMO_DATA["users"]:
            try:
                self.service.register_user(username, password, role)
            except ValueError:
                pass  # User already exists

        # Members
        for name, email, phone in DEMO_DATA["members"]:
            self.service.add_member(name, email, phone)

        # Books
        for title, author, isbn, copies in DEMO_DATA["books"]:
            try:
                self.service.add_book(title, author, isbn, copies)
            except ValueError:
                pass  # Book already exists

        print("Demo data seeded!\n")

    def _login_menu(self):
        """Login screen."""
        print("\n=== Library Management System ===")
        print("1. Login")
        print("2. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = self.service.authenticate(username, password)
            if user:
                self.current_user = user
                print(f"\nWelcome, {user.username} ({user.role})!")
            else:
                print("\nInvalid credentials.")
        elif choice == "2":
            print("Goodbye!")
            exit()

    def _admin_menu(self):
        """Admin menu."""
        print("\n=== Admin Menu ===")
        print("1. Add book")
        print("2. Edit book")
        print("3. Delete book")
        print("4. List books")
        print("5. Add member")
        print("6. Edit member")
        print("7. Delete member")
        print("8. List members")
        print("9. Create librarian")
        print("10. View active loans")
        print("11. View summary report")
        print("12. Bulk import books")
        print("13. Logout")
        choice = input("Choice: ").strip()

        if choice == "1":
            self._add_book()
        elif choice == "2":
            self._edit_book()
        elif choice == "3":
            self._delete_book()
        elif choice == "4":
            self._list_books()
        elif choice == "5":
            self._add_member()
        elif choice == "6":
            self._edit_member()
        elif choice == "7":
            self._delete_member()
        elif choice == "8":
            self._list_members()
        elif choice == "9":
            self._create_librarian()
        elif choice == "10":
            self._view_active_loans()
        elif choice == "11":
            self._view_summary_report()
        elif choice == "12":
            self._bulk_import()
        elif choice == "13":
            self.current_user = None

    def _librarian_menu(self):
        """Librarian menu."""
        print("\n=== Librarian Menu ===")
        print("1. Issue book")
        print("2. Return book")
        print("3. Search books by title")
        print("4. Search books by author")
        print("5. List all books")
        print("6. View active loans")
        print("7. View summary report")
        print("8. Logout")
        choice = input("Choice: ").strip()

        if choice == "1":
            self._issue_book()
        elif choice == "2":
            self._return_book()
        elif choice == "3":
            self._search_by_title()
        elif choice == "4":
            self._search_by_author()
        elif choice == "5":
            self._list_books()
        elif choice == "6":
            self._view_active_loans()
        elif choice == "7":
            self._view_summary_report()
        elif choice == "8":
            self.current_user = None

    def _add_book(self):
        """Add a book."""
        try:
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            isbn = input("ISBN: ").strip()
            copies = int(input("Copies: ").strip())
            book = self.service.add_book(title, author, isbn, copies)
            print(f"\nBook added: {book.title} (ID: {book.id})")
        except ValueError as e:
            print(f"\nError: {e}")

    def _edit_book(self):
        """Edit a book."""
        try:
            book_id = int(input("Book ID: ").strip())
            book = self.service.get_book(book_id)
            if not book:
                print("\nBook not found.")
                return
            title = input(f"Title ({book.title}): ").strip() or book.title
            author = input(f"Author ({book.author}): ").strip() or book.author
            isbn = input(f"ISBN ({book.isbn}): ").strip() or book.isbn
            copies = input(f"Copies ({book.copies_available}): ").strip()
            copies = int(copies) if copies else book.copies_available
            updated = self.service.update_book(book_id, title, author, isbn, copies)
            print(f"\nBook updated: {updated.title}")
        except ValueError as e:
            print(f"\nError: {e}")

    def _delete_book(self):
        """Delete a book."""
        try:
            book_id = int(input("Book ID: ").strip())
            self.service.delete_book(book_id)
            print("\nBook deleted.")
        except ValueError as e:
            print(f"\nError: {e}")

    def _list_books(self):
        """List all books."""
        books = self.service.list_books()
        if not books:
            print("\nNo books found.")
            return
        print("\nBooks:")
        print("-" * 100)
        print(f"{'ID':<5} {'Title':<30} {'Author':<25} {'ISBN':<15} {'Available':<10}")
        print("-" * 100)
        for book in books:
            print(f"{book.id:<5} {book.title:<30} {book.author:<25} {book.isbn:<15} {book.copies_available:<10}")
        print("-" * 100)

    def _add_member(self):
        """Add a member."""
        try:
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            member = self.service.add_member(name, email, phone)
            print(f"\nMember added: {member.name} (ID: {member.id})")
        except ValueError as e:
            print(f"\nError: {e}")

    def _edit_member(self):
        """Edit a member."""
        try:
            member_id = int(input("Member ID: ").strip())
            member = self.service.get_member(member_id)
            if not member:
                print("\nMember not found.")
                return
            name = input(f"Name ({member.name}): ").strip() or member.name
            email = input(f"Email ({member.email}): ").strip() or member.email
            phone = input(f"Phone ({member.phone}): ").strip() or member.phone
            updated = self.service.update_member(member_id, name, email, phone)
            print(f"\nMember updated: {updated.name}")
        except ValueError as e:
            print(f"\nError: {e}")

    def _delete_member(self):
        """Delete a member."""
        try:
            member_id = int(input("Member ID: ").strip())
            self.service.delete_member(member_id)
            print("\nMember deleted.")
        except ValueError as e:
            print(f"\nError: {e}")

    def _list_members(self):
        """List all members."""
        members = self.service.list_members()
        if not members:
            print("\nNo members found.")
            return
        print("\nMembers:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<30} {'Email':<30} {'Phone':<15}")
        print("-" * 80)
        for member in members:
            print(f"{member.id:<5} {member.name:<30} {member.email:<30} {member.phone:<15}")
        print("-" * 80)

    def _create_librarian(self):
        """Create a new librarian."""
        try:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = self.service.register_user(username, password, "librarian")
            print(f"\nLibrarian created: {user.username}")
        except ValueError as e:
            print(f"\nError: {e}")

    def _issue_book(self):
        """Issue a book to a member."""
        try:
            print("\nSelect member:")
            members = self.service.list_members()
            if not members:
                print("No members found.")
                return
            for m in members:
                print(f"{m.id}: {m.name}")
            member_id = int(input("Member ID: ").strip())

            print("\nSelect book:")
            books = self.service.list_books()
            if not books:
                print("No books found.")
                return
            available = [b for b in books if b.copies_available > 0]
            if not available:
                print("No available books.")
                return
            for b in available:
                print(f"{b.id}: {b.title} ({b.copies_available} available)")
            book_id = int(input("Book ID: ").strip())

            loan = self.service.issue_book(member_id, book_id)
            print(f"\nBook issued. Due: {loan.due_date}")
        except ValueError as e:
            print(f"\nError: {e}")

    def _return_book(self):
        """Return a book."""
        try:
            loans = self.service.list_active_loans()
            if not loans:
                print("\nNo active loans.")
                return
            print("\nActive loans:")
            for loan in loans:
                member = self.service.get_member(loan.member_id)
                book = self.service.get_book(loan.book_id)
                print(f"{loan.id}: {member.name} - {book.title} (Due: {loan.due_date})")
            loan_id = int(input("Loan ID: ").strip())
            returned = self.service.return_book(loan_id)
            print(f"\nBook returned.")
        except ValueError as e:
            print(f"\nError: {e}")

    def _search_by_title(self):
        """Search books by title."""
        title = input("Search title: ").strip()
        books = self.service.search_books_by_title(title)
        if books:
            self._print_books_table(books)
        else:
            print("\nNo books found.")

    def _search_by_author(self):
        """Search books by author."""
        author = input("Search author: ").strip()
        books = self.service.search_books_by_author(author)
        if books:
            self._print_books_table(books)
        else:
            print("\nNo books found.")

    def _view_active_loans(self):
        """View active loans."""
        loans = self.service.list_active_loans()
        if not loans:
            print("\nNo active loans.")
            return
        print("\nActive Loans:")
        print("-" * 120)
        print(f"{'ID':<5} {'Member':<30} {'Book':<30} {'Issued':<12} {'Due':<12}")
        print("-" * 120)
        for loan in loans:
            member = self.service.get_member(loan.member_id)
            book = self.service.get_book(loan.book_id)
            print(
                f"{loan.id:<5} {member.name:<30} {book.title:<30} {loan.issue_date:<12} {loan.due_date:<12}"
            )
        print("-" * 120)

    def _view_summary_report(self):
        """View summary report."""
        from library_system.reports import LibraryReporter

        reporter = LibraryReporter(self.service)
        reporter.print_summary()

    def _bulk_import(self):
        """Bulk import books from CSV."""
        try:
            csv_path = input("CSV file path: ").strip()
            count = self.service.bulk_import_books(csv_path)
            print(f"\n{count} books imported.")
        except ValueError as e:
            print(f"\nError: {e}")

    def _print_books_table(self, books):
        """Helper to print books table."""
        print("\nBooks:")
        print("-" * 100)
        print(f"{'ID':<5} {'Title':<30} {'Author':<25} {'ISBN':<15} {'Available':<10}")
        print("-" * 100)
        for book in books:
            print(f"{book.id:<5} {book.title:<30} {book.author:<25} {book.isbn:<15} {book.copies_available:<10}")
        print("-" * 100)
