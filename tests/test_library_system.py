import os
import tempfile
import unittest

from library_system.database import LibraryRepository
from library_system.service import LibraryService


class LibrarySystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "library_test.db")
        self.repo = LibraryRepository(self.db_path)
        self.repo.init_db()
        self.service = LibraryService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_and_authenticate(self):
        user = self.service.register_user("admin1", "admin123", "admin")
        self.assertEqual(user.role, "admin")
        self.assertIsNotNone(self.service.authenticate("admin1", "admin123"))
        self.assertIsNone(self.service.authenticate("admin1", "wrongpass"))

    def test_book_crud(self):
        book = self.service.add_book("Test Book", "Tester", "9780000000001", 3)
        self.assertEqual(book.copies_available, 3)

        fetched = self.service.get_book(book.id)
        self.assertEqual(fetched.title, "Test Book")

        updated = self.service.update_book(book.id, "Updated Title", "Tester", "9780000000001", 5)
        self.assertEqual(updated.copies_available, 5)

        results = self.service.search_books("title", "updated")
        self.assertTrue(any(item.title == "Updated Title" for item in results))

        self.service.delete_book(book.id)
        self.assertIsNone(self.service.get_book(book.id))

    def test_member_crud(self):
        member = self.service.add_member("Jane Doe", "jane@example.com", "555-1111")
        self.assertEqual(member.name, "Jane Doe")

        fetched = self.service.get_member(member.id)
        self.assertEqual(fetched.email, "jane@example.com")

        updated = self.service.update_member(member.id, "Jane Smith", "jane@example.com", "555-2222")
        self.assertEqual(updated.phone, "555-2222")

    def test_issue_and_return_book(self):
        member = self.service.add_member("Sam Reader", "sam@example.com", "555-3333")
        book = self.service.add_book("Book Alpha", "Author A", "9780000000002", 1)

        loan = self.service.issue_book(member.id, book.id)
        self.assertIsNotNone(loan)
        self.assertEqual(self.service.get_book(book.id).copies_available, 0)

        returned = self.service.return_book(loan.id)
        self.assertIsNotNone(returned.return_date)
        self.assertEqual(self.service.get_book(book.id).copies_available, 1)

    def test_import_csv(self):
        temp_csv = os.path.join(self.temp_dir.name, "books.csv")
        with open(temp_csv, "w", newline="", encoding="utf-8") as handle:
            handle.write("title,author,isbn,copies\n")
            handle.write("CSV Book,CSV Author,9780000000003,2\n")
            handle.write("Second CSV Book,Another Author,9780000000004,1\n")

        imported = self.service.import_books_from_csv(temp_csv)
        self.assertEqual(imported, 2)
        self.assertEqual(len(self.service.list_books()), 2)

    def test_generate_report(self):
        member = self.service.add_member("Librarian User", "lib@example.com", "555-4444")
        book = self.service.add_book("Report Book", "Some Author", "9780000000005", 2)
        loan = self.service.issue_book(member.id, book.id)

        report = self.service.generate_report(os.path.join(self.temp_dir.name, "report.png"))
        self.assertGreater(report["total_loans"], 0)
        self.assertTrue(os.path.exists(report["chart_path"]))
        self.service.return_book(loan.id)


if __name__ == "__main__":
    unittest.main()
