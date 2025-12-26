import json
import os
import sys
from numbers import Number
from typing import List, Dict

FILE_PATH = "books.json"

BookValue = str | int | None
Book = Dict[str, BookValue]

def load_books() -> List[Book]:
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_books(books: List[Book]) -> None:
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=4, ensure_ascii=False)


def next_id(books: List[Book]) -> int:
    return max((book["id"] for book in books), default=0) + 1


def remove_book(book_id: int) -> bool:
    books = load_books()
    filtered = [b for b in books if b["id"] != book_id]

    if len(books) == len(filtered):
        return False

    save_books(filtered)
    return True

def _parse_new_value(current: BookValue, raw: str) -> tuple[bool, BookValue]:
    """
    Returns (should_update, new_value).
    - raw == "" or raw == " " -> do not update
    - raw == "null" -> update to None
    - if current is int OR raw looks like an int -> update to int
    - else update to str
    """
    # Skip on Enter or single space (your requirement)
    if raw == "" or raw == " ":
        return False, current

    if raw.strip().lower() == "null":
        return True, None

    candidate = raw.strip()

    # If current is numeric, prefer numeric parsing
    if isinstance(current, int):
        try:
            return True, int(candidate)
        except ValueError:
            # If user typed non-number, keep as string (or you can reject)
            return True, candidate

    # If user typed a number, store as int
    if candidate.isdigit() or (candidate.startswith("-") and candidate[1:].isdigit()):
        return True, int(candidate)

    return True, candidate

def update_book(book_id: int | None, book: Book) -> Book | None:
    if book_id is None:
        print("No ID selected. Choose another ID or exit to menu.")
        return None

    books = load_books()

    for idx , existing in enumerate(books):
        if existing.get("id") == book_id:
            print(f'Chosen ID: {existing["id"]} - {existing["author"]} - {existing["title"]}')
            print('Press Space or Enter to skip category, type "null" to clear field')

            for key in list(existing.keys()):
                if key == "id":
                    continue

                current_value = existing.get(key)
                print(f'{key}: {current_value}')

                raw = input("New value: ")
                should_update, new_value = _parse_new_value(current_value, raw)

                if should_update:
                    existing[key] = new_value

            books[idx] = existing
            save_books(books)

            print("Book updated.")
            return existing

        print("No book found with this ID. Choose another ID or exit to menu.")
        return None
    return None


def list_books() -> None:
    books = load_books()

    if not books:
        print("No books found.")
        return

    last_index = len(books) - 1

    for i, b in enumerate(books):
        line = (
            f'{b["id"]}. {b["author"]} - {b["title"]} ' 
            f'/ {b["series"]} - {b["numberInSeries"]}'
            f'/ {b["subSeries"]} - {b["numberInSubSeries"]}'
            f'/ {b["format"]} / {b["language"]} / {b["year"]}'
        )

        print(line)

        if i == last_index:
            print("-" * len(line))


def menu():
    while True:
        print("1. List all books")
        print("2. Add book")
        print("3. Update book")
        print("4. Remove book")
        print("5. Exit")
        choice = input("Enter number : ")
        if choice == "1":
            list_books()
        elif choice == "2":
            remove_book(book_id=0)
        elif choice == "3":

            print("1. Choose id")
            print("2. Return main menu")
            choice = input("Enter number : ")
            while True:
                if choice == "1":
                    book_id = int(input("Enter book ID : "))
                    update_book(book_id, Book(book_id))
                else: break

            pass
        elif choice == "4":
            remove_book(next_id(load_books()))
        elif choice == "5":
            sys.exit(0)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()

