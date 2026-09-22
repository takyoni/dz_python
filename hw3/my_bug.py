"""Задание 2: собственный баг-репорт (изменяемость / hashable)."""

# --- 1. Багованный код ------------------------------------------------------


class Tag:
    """Тег книги. Хеш считается по изменяемому полю name."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Tag) and self.name == other.name


def run_buggy() -> None:
    counters = {Tag("proza"): 12}
    tag = next(iter(counters))
    tag.name = "poetry"  # опечатку "исправили" уже после вставки в словарь

    print("ключей в словаре:", len(counters))          # 1
    print("ищем Tag('poetry'):", Tag("poetry") in counters)  # False
    print("ищем Tag('proza'):", Tag("proza") in counters)    # тоже False
    print("а перебором он есть:", [t.name for t in counters])  # ['poetry']


# --- 2. Что происходит и почему --------------------------------------------
#
# Объект Tag формально hashable (у него есть __hash__), но его хеш зависит от
# изменяемого атрибута name. Словарь разложил ключ по корзине в момент вставки
# по hash("proza") и больше эту корзину не пересчитывает, поэтому после правки
# name ключ лежит "не в своей" корзине: по новому значению поиск идёт в другую
# корзину и ничего не находит, а по старому — находит корзину, но не проходит
# сравнение __eq__. Ключ становится недостижим по любому запросу, хотя при
# переборе словаря он прекрасно виден.


# --- 3. Исправленная версия -------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True)
class FrozenTag:
    """Тот же тег, но неизменяемый: hash навсегда согласован с полем name."""

    name: str


def run_fixed() -> None:
    counters = {FrozenTag("proza"): 12}

    # Переименование — это создание нового ключа и явный перенос значения,
    # а не тихая правка объекта внутри словаря.
    old = FrozenTag("proza")
    new = FrozenTag("poetry")
    counters[new] = counters.pop(old)

    print("ключей в словаре:", len(counters))                 # 1
    print("ищем FrozenTag('poetry'):", new in counters)       # True
    print("ищем FrozenTag('proza'):", old in counters)        # False, и это честно
    print("перебором:", [t.name for t in counters])           # ['poetry']

    # Попытка испортить ключ теперь падает сразу, а не портит словарь молча:
    try:
        new.name = "drama"
    except AttributeError as exc:
        print("изменить ключ нельзя:", exc)


if __name__ == "__main__":
    print("--- багованная версия ---")
    run_buggy()
    print("\n--- исправленная версия ---")
    run_fixed()
