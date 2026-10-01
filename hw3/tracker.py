"""Трекер домашней библиотеки.

Задание 1: выбор коллекций (list / tuple / dict / set).
Почему выбрал именно так - в README.txt рядом.
"""

from __future__ import annotations

import copy
from typing import Iterable, Iterator

# Одна книга - это кортеж (id, title, year).
# Номера полей вынес в константы, чтобы не писать book[2] и не путаться.
ID, TITLE, YEAR = 0, 1, 2

Book = tuple[int, str, int]


class Library:
    """Книги в списке + словарь для поиска по id + множество жанров."""

    def __init__(self, books: Iterable[Book] | None = None) -> None:
        # По умолчанию None, а не [] - иначе один список был бы общим
        # для всех объектов Library.
        self._books: list[Book] = list(books) if books is not None else []
        # Словарь id -> книга, чтобы не перебирать список при каждом поиске.
        self._by_id: dict[int, Book] = {book[ID]: book for book in self._books}
        # Жанры - множество: нужен только факт "есть/нет", без повторов.
        self._genres: set[str] = set()

    # добавление/удаление

    def add(self, book_id: int, title: str, year: int, genres: Iterable[str] = ()) -> Book:
        """Добавить книгу и вернуть её."""
        if book_id in self._by_id:
            raise ValueError(f"книга с id={book_id} уже есть")

        book: Book = (book_id, title, year)
        self._books.append(book)
        self._by_id[book_id] = book
        # Кортеж менять нельзя, поэтому не страшно, что одна и та же книга
        # лежит и в списке, и в словаре.
        self._genres.update(genres)
        return book

    def remove(self, book_id: int) -> Book:
        """Удалить книгу по id."""
        book = self._by_id.pop(book_id, None)
        if book is None:
            raise KeyError(f"книги с id={book_id} нет")
        self._books.remove(book)
        return book

    def remove_older_than(self, year: int) -> list[Book]:
        """Удалить книги старше указанного года."""
        # Не удаляю из списка пока иду по нему - собираю новый.
        dropped = [book for book in self._books if book[YEAR] < year]
        self._books = [book for book in self._books if book[YEAR] >= year]
        for book in dropped:
            del self._by_id[book[ID]]
        return dropped

    # чтение

    def get(self, book_id: int) -> Book | None:
        """Найти книгу по id."""
        return self._by_id.get(book_id)

    def all_books(self) -> list[Book]:
        """Копия списка книг.

        Отдаю копию, а не сам список - иначе снаружи можно было бы
        поменять библиотеку в обход методов.
        """
        return list(self._books)

    def genres(self) -> set[str]:
        """Копия множества жанров, по той же причине."""
        return set(self._genres)

    def titles_by_year(self) -> dict[int, list[str]]:
        """Названия книг по годам."""
        grouped: dict[int, list[str]] = {}
        for book in self._books:
            # setdefault заводит отдельный список под каждый год.
            grouped.setdefault(book[YEAR], []).append(book[TITLE])
        return grouped

    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self) -> Iterator[Book]:
        return iter(self._books)


def merge_shelves(first: Library, second: Library) -> Library:
    """Склеить две библиотеки в новую, исходные не трогаем."""
    merged = Library(first.all_books())
    for book in second:
        if merged.get(book[ID]) is None:
            merged.add(*book)
    return merged


def main() -> None:
    library = Library()
    library.add(1, "Дюна", 1965, genres=["фантастика"])
    library.add(2, "Солярис", 1961, genres=["фантастика", "философия"])
    library.add(3, "Хоббит", 1937, genres=["фэнтези"])

    print("Всего книг:", len(library))
    print("Поиск по id=2:", library.get(2))
    print("Жанры:", sorted(library.genres()))
    print("По годам:", library.titles_by_year())

    # Меняем копию - библиотека не меняется.
    snapshot = library.all_books()
    snapshot.append((99, "Подделка", 2024))
    print("После правки копии в библиотеке по-прежнему:", len(library), "книг")

    dropped = library.remove_older_than(1960)
    print("Убрали старые:", dropped)
    print("Осталось:", library.all_books())

    # Для вложенных структур нужен deepcopy, иначе внутренние списки общие.
    grouped = library.titles_by_year()
    grouped_backup = copy.deepcopy(grouped)
    grouped_backup[1965].append("случайно дописали")
    print("Оригинал не изменился:", grouped)


if __name__ == "__main__":
    main()
