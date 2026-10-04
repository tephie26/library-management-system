from datetime import date, timedelta
from typing import List, Dict
import matplotlib.pyplot as plt
import pandas as pd


class LibraryReporter:
    """Generates reports and visualizations."""

    def __init__(self, service):
        self.service = service

    def get_summary_stats(self) -> Dict:
        """Get summary statistics."""
        books = self.service.list_books()
        members = self.service.list_members()
        loans = self.service.list_loans()
        active_loans = self.service.list_active_loans()

        total_copies = sum(b.copies_available for b in books)
        total_books = len(books)
        
        return {
            "total_books": total_books,
            "total_members": len(members),
            "total_loans": len(loans),
            "active_loans": len(active_loans),
            "available_copies": total_copies,
            "books": books,
            "loans": loans,
            "active_loans_list": active_loans,
        }

    def print_summary(self):
        """Print a text summary report."""
        stats = self.get_summary_stats()
        
        print("\n" + "=" * 60)
        print("LIBRARY SUMMARY REPORT")
        print("=" * 60)
        print(f"Total Books: {stats['total_books']}")
        print(f"Total Members: {stats['total_members']}")
        print(f"Total Loans (all time): {stats['total_loans']}")
        print(f"Active Loans: {stats['active_loans']}")
        print(f"Available Copies: {stats['available_copies']}")
        print("=" * 60)

        # Most popular books
        print("\nMost Popular Books (by loan count):")
        popular = self._get_popular_books()
        for title, count in popular:
            print(f"  {title}: {count} loans")

        # Overdue
        print("\nOverdue Books (by due_date):")
        overdue = self._get_overdue_loans()
        if overdue:
            for loan in overdue:
                member = self.service.get_member(loan.member_id)
                book = self.service.get_book(loan.book_id)
                print(f"  {member.name} - {book.title} (Due: {loan.due_date})")
        else:
            print("  No overdue books.")

        # Chart
        self._plot_loans_by_book()

    def _get_popular_books(self) -> List[tuple]:
        """Get most popular books (by loan count)."""
        loans = self.service.list_loans()
        book_counts = {}
        for loan in loans:
            book = self.service.get_book(loan.book_id)
            book_counts[book.title] = book_counts.get(book.title, 0) + 1
        
        sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_books[:5]  # Top 5

    def _get_overdue_loans(self) -> List:
        """Get overdue loans."""
        today = date.today()
        return [
            loan for loan in self.service.list_active_loans()
            if loan.due_date < today
        ]

    def _plot_loans_by_book(self):
        """Plot loans by book (bar chart)."""
        popular = self._get_popular_books()
        if not popular:
            print("\nNo loan data to display.")
            return

        titles, counts = zip(*popular)
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(titles)), counts, color='steelblue')
        plt.xticks(range(len(titles)), titles, rotation=45, ha='right')
        plt.ylabel('Number of Loans')
        plt.title('Most Popular Books')
        plt.tight_layout()
        
        # Save plot
        plt.savefig('library_report.png', dpi=100, bbox_inches='tight')
        print("\nChart saved: library_report.png")
        plt.show()
