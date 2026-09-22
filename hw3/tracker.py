"""Трекер домашней библиотеки.

Задание 1: осознанный выбор коллекций (list / tuple / dict / set).
Обоснование выбора — в README.md рядом с этим файлом.
"""

from __future__ import annotations

import copy
from typing import Iterable, Iterator

# Одна запись о книге — кортеж фиксированной структуры:
# (book_id, title, year). Индексы полей вынесены в константы,
# чтобы не было "магических" чисел в коде.
ID, TITLE, YEAR = 0, 1, 2

Book = tuple[int, str, int]


class Library:
    """Хранилище книг: список записей + индекс по id + множество жанров."""

    def __init__(self, books: Iterable[Book] | None = None) -> None:
        # Значение по умолчанию — None, а не [] или {}:
        # изменяемый объект в сигнатуре создаётся один раз при определении
        # функции и был бы общим для всех экземпляров Library.
        self._books: list[Book] = list(books) if books is not None else []
        # dict: id -> запись, чтобы искать за O(1), а не пробегать список.
        self._by_id: dict[int, Book] = {book[ID]: book for book in self._books}
        # set: жанры, у которых важен только факт наличия, без порядка и повторов.
        self._genres: set[str] = set()

    # --- изменение состояния -------------------------------------------------

    def add(self, book_id: int, title: str, year: int, genres: Iterable[str] = ()) -> Book:
        """Добавить книгу. Возвращает созданную запись."""
        if book_id in self._by_id:
            raise ValueError(f"книга с id={book_id} уже есть")

        book: Book = (book_id, title, year)
        self._books.append(book)
        self._by_id[book_id] = book
        # Кортеж неизменяем, поэтому одна и та же запись спокойно лежит
        # и в списке, и в словаре: "поменять" её через одну ссылку нельзя.
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
        """Удалить все книги старше указанного года."""
        # Список не изменяется во время прохода по нему: сначала собираем
        # то, что уходит, затем пересобираем список целиком.
        dropped = [book for book in self._books if book[YEAR] < year]
        self._books = [book for book in self._books if book[YEAR] >= year]
        for book in dropped:
            del self._by_id[book[ID]]
        return dropped

    # --- чтение --------------------------------------------------------------

    def get(self, book_id: int) -> Book | None:
        """Быстрый поиск по ключу."""
        return self._by_id.get(book_id)

    def all_books(self) -> list[Book]:
        """Копия списка записей.

        Возвращаем именно копию: иначе вызывающий код получил бы алиас
        внутреннего списка и мог бы менять состояние библиотеки в обход методов.
        """
        return list(self._books)

    def genres(self) -> set[str]:
        """Копия множества жанров — по той же причине, что и all_books()."""
        return set(self._genres)

    def titles_by_year(self) -> dict[int, list[str]]:
        """Сгруппировать названия по году издания."""
        grouped: dict[int, list[str]] = {}
        for book in self._books:
            # setdefault создаёт новый список под каждый год,
            # а не переиспользует один общий.
            grouped.setdefault(book[YEAR], []).append(book[TITLE])
        return grouped

    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self) -> Iterator[Book]:
        return iter(self._books)


def merge_shelves(first: Library, second: Library) -> Library:
    """Собрать новую библиотеку из двух, не трогая исходные."""
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

    # Изменение копии не задевает саму библиотеку.
    snapshot = library.all_books()
    snapshot.append((99, "Подделка", 2024))
    print("После правки копии в библиотеке по-прежнему:", len(library), "книг")

    dropped = library.remove_older_than(1960)
    print("Убрали старьё:", dropped)
    print("Осталось:", library.all_books())

    # Вложенные структуры копируем глубоко, если нужна независимая версия.
    grouped = library.titles_by_year()
    grouped_backup = copy.deepcopy(grouped)
    grouped_backup[1965].append("случайно дописали")
    print("Оригинал не изменился:", grouped)


if __name__ == "__main__":
    main()
