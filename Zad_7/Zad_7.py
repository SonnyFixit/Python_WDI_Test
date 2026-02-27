import re
from itertools import permutations
from typing import Dict, List, Tuple

# Równanie w formacie: <LICZBA><OP><LICZBA>=<LICZBA>, gdzie liczby są z liter A-J
EQ_RE = re.compile(r"^\s*([A-J]+)\s*([\+\-\*/])\s*([A-J]+)\s*=\s*([A-J]+)\s*$")


def parse_equation(expr: str) -> Tuple[str, str, str, str]:
    """Parsuje wejście i zwraca trzy „liczby” literowe oraz operator."""
    m = EQ_RE.match(expr.upper())
    if not m:
        raise ValueError(
            "Błędny format. Podaj w formacie: <LICZBA> <OP> <LICZBA> = <LICZBA>, "
            "gdzie liczby są z liter A-J, np. ABC*BD=EFGAH"
        )
    left1, op, left2, right = m.group(1), m.group(2), m.group(3), m.group(4)
    return left1, op, left2, right


def letters_in_order(parts: List[str]) -> List[str]:
    """Zbiera litery występujące w równaniu, zachowując kolejność pierwszego wystąpienia."""
    seen = set()
    out = []
    for p in parts:
        for ch in p:
            if ch not in seen:
                seen.add(ch)
                out.append(ch)
    return out


def word_to_int(word: str, mapping: Dict[str, int]) -> int:
    """Zamienia „liczbę” literową na liczbę całkowitą według aktualnego mapowania liter na cyfry."""
    return int("".join(str(mapping[ch]) for ch in word))


def eval_equation(a: int, op: str, b: int, c: int) -> bool:
    """Sprawdza,\ czy równanie a <op> b = c jest spełnione."""
    if op == "+":
        return a + b == c
    if op == "-":
        return a - b == c
    if op == "*":
        return a * b == c
    if op == "/":
        # Dzielenie bez reszty
        return b != 0 and a == b * c
    raise ValueError("Nieobsługiwany operator.")


def solve(expr: str, limit: int | None = None) -> List[Dict[str, int]]:
    """
    Rozwiązuje zagadkę przez brute-force:
    - wybiera wszystkie możliwe przypisania cyfr 0..9 do użytych liter,
    - pilnuje zakazu zer wiodących dla liczb wieloliterowych,
    - sprawdza równanie po podstawieniu.
    """
    w1, op, w2, w3 = parse_equation(expr)
    words = [w1, w2, w3]

    # Lista użytych liter (maksymalnie 10)
    letters = letters_in_order(words)
    if len(letters) > 10:
        raise ValueError(f"Za dużo różnych liter ({len(letters)}). Maksymalnie 10 (A-J).")

    # Litery stojące na początku wielocyfrowej liczby nie mogą być zerem
    leading = {w[0] for w in words if len(w) > 1}

    solutions: List[Dict[str, int]] = []
    digits = range(10)

    # permutations daje różne cyfry dla różnych liter (bez powtórzeń)
    for perm in permutations(digits, len(letters)):
        mapping = dict(zip(letters, perm))

        # Odrzucamy mapowania z zerem wiodącym
        if any(mapping[ch] == 0 for ch in leading):
            continue

        # Zamiana słów literowych na liczby
        a = word_to_int(w1, mapping)
        b = word_to_int(w2, mapping)
        c = word_to_int(w3, mapping)

        # Sprawdzenie równania
        if eval_equation(a, op, b, c):
            solutions.append(mapping.copy())

            # Jeśli ustawiono limit, kończymy po znalezieniu tylu rozwiązań
            if limit is not None and len(solutions) >= limit:
                break

    return solutions


def format_solution(expr: str, mapping: Dict[str, int]) -> str:
    w1, op, w2, w3 = parse_equation(expr)

    a = word_to_int(w1, mapping)
    b = word_to_int(w2, mapping)
    c = word_to_int(w3, mapping)

    # Mapowanie typu: A=6, B=2, ...
    items = ", ".join(f"{k}={mapping[k]}" for k in sorted(mapping.keys()))

    # Podstawienia dla całych lioczb literowych
    subst = f"{w1}={a}, {w2}={b}, {w3}={c}"

    # Pełne równanie w wersji literowej i liczbowej
    eq_letters = f"{w1} {op} {w2} = {w3}"
    eq_numbers = f"{a} {op} {b} = {c}"

    return (
        f"{items}\n"
        f"Podstawienia: {subst}\n"
        f"Równanie (litery): {eq_letters}\n"
        f"Równanie (cyfry) : {eq_numbers}"
    )


def main() -> None:
    # Input z klawiatury w formacie opisanym w zadaniu
    expr = input("Podaj równanie (np. ABC*BD=EFGAH): ").strip()

    try:
        # limit=None -> wypisz wszystkie rozwiązania
        sols = solve(expr, limit=None)
    except ValueError as e:
        print(f"Błąd: {e}")
        return

    if not sols:
        print("Brak rozwiązań.")
        return

    print(f"\nZnaleziono rozwiązań: {len(sols)}\n")

    # Wypisujemy każde znalezione mapowanie i odpowiadające mu równanie liczbowe
    for i, mapping in enumerate(sols, 1):
        print(f"--- Rozwiązanie {i} ---")
        print(format_solution(expr, mapping))
        print()


if __name__ == "__main__":
    main()