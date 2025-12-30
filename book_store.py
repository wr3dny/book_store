import json
import os
import sys
from numbers import Number
from typing import List, Dict, Optional

FILE_PATH = "books.json"

BookValue = str | int | None
Book = Dict[str, BookValue]

BOOK_FIELDS: list[tuple[str, str]] = [
    ("author", "Author"),
    ("title", "Title"),
    ("series", "Series"),
    ("numberInSeries", "Number in Series"),
    ("subSeries", "Sub-Series"),
    ("numberInSubSeries", "Number in Sub-Series"),
    ("format", "Format"),
    ("language", "Language"),
]


def load_books() -> List[Book]:
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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
            f'/ {b["format"]} / {b["language"]} '
        )

        print(line)

        if i == last_index:
            print("-" * len(line))


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

    if raw == "" or raw == " ":
        return False, current

    if raw.strip().lower() == "null":
        return True, None

    candidate = raw.strip()

    if isinstance(current, int):
        try:
            return True, int(candidate)
        except ValueError:
            return True, candidate

    if candidate.isdigit() or (candidate.startswith("-") and candidate[1:].isdigit()):
        return True, int(candidate)

    return True, candidate


def _parse_int_or_none(raw: str) -> Optional[int]:
    s = raw.strip()
    if s == "":
        return None
    if s.lower() == "null":
        return None
    try:
        return int(s)
    except ValueError:
        return None


def add_book() -> Book:
    books = load_books()
    new_book_id = next_id(books)

    book: Book = {"id": new_book_id}

    print(f"Adding new book with ID: {new_book_id}")
    print('Press Space or Enter to skip category, type "null" to leave field empty')

    for key, label in BOOK_FIELDS:
        raw = input(f"{label}: ").strip()

        if raw.lower() == "null" or raw == "":
            value: BookValue = None
        else:
            if key in {"numberInSeries", "numberInSubSeries"}:
                parsed = _parse_int_or_none(raw)
                value = parsed
            else:
                value = raw
                
        book[key] = value

    books.append(book)
    save_books(books)
    print("Book added.")
    return book


def update_book(book_id: int | None) -> Book | None:
    if book_id is None:
        print("No ID selected. Choose another ID or exit to menu.")
        return None

    books = load_books()

    for idx, existing in enumerate(books):
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


def menu():
    while True:
        print("Book Store Menu")
        print("1. List all books")
        print("2. Add book")
        print("3. Update book")
        print("4. Remove book")
        print("5. Exit")

        choice = input("Enter number : ")

        if choice == "1":
            list_books()

        elif choice == "2":
            add_book()

        elif choice == "3":
            while True:
                print("1. Choose id")
                print("2. Return main menu")
                sub = input("Enter number : ").strip()
                if sub == "1":
                    try:
                        book_id = int(input("Enter book ID: ").strip())
                    except ValueError:
                        print("Invalid ID.")
                        continue
                    update_book(book_id)
                elif sub == "2":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "4":
            try:
                book_id = int(input("Enter book ID to remove: ").strip())
            except ValueError:
                print("Invalid ID.")
                continue

            if remove_book(book_id):
                print("Book removed.")
            else:
                print("No book found with this ID.")

        elif choice == "5":
            sys.exit(0)
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()
