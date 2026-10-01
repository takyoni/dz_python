"""Задание 2: мой баг про изменяемость и hashable."""

# --- 1. Код с багом


class Tag:
    """Тег книги. Хеш считается по полю name, а name можно менять."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Tag) and self.name == other.name


def run_buggy() -> None:
    counters = {Tag("proza"): 12}
    tag = next(iter(counters))
    tag.name = "poetry"  # заметил опечатку и поправил прямо в ключе

    print("ключей в словаре:", len(counters))                 # 1
    print("ищем Tag('poetry'):", Tag("poetry") in counters)   # False
    print("ищем Tag('proza'):", Tag("proza") in counters)     # тоже False
    print("а перебором он есть:", [t.name for t in counters])  # ['poetry']


# --- 2. Что пошло не так 
#
# У Tag есть __hash__, так что словарь его принимает. Но хеш зависит от name,
# а name потом поменяли. Словарь положил ключ в корзину по hash("proza") и
# после этого ничего не пересчитывает. В итоге:
#  - ищем по "poetry" -> идём в другую корзину, там пусто;
#  - ищем по "proza"  -> корзина та, но __eq__ сравнивает "proza" с "poetry"
#    и говорит нет.
# Ключ в словаре есть (видно при переборе), но достать его уже никак.


# --- 3. Как починил

from dataclasses import dataclass


@dataclass(frozen=True)
class FrozenTag:
    """Тот же тег, но менять его нельзя, поэтому хеш не разъедется с name."""

    name: str


def run_fixed() -> None:
    counters = {FrozenTag("proza"): 12}

    # Переименовать = завести новый ключ и перенести в него значение.
    # Старый объект не трогаем.
    old = FrozenTag("proza")
    new = FrozenTag("poetry")
    counters[new] = counters.pop(old)

    print("ключей в словаре:", len(counters))            # 1
    print("ищем FrozenTag('poetry'):", new in counters)  # True
    print("ищем FrozenTag('proza'):", old in counters)   # False, так и должно быть
    print("перебором:", [t.name for t in counters])      # ['poetry']

    # Если попробовать поменять ключ, упадёт сразу, а не сломает словарь тихо.
    try:
        new.name = "drama"
    except AttributeError as exc:
        print("изменить ключ нельзя:", exc)


if __name__ == "__main__":
    print("--- версия с багом ---")
    run_buggy()
    print("\n--- исправленная версия ---")
    run_fixed()
