from __future__ import annotations

import math
import sys
from time import perf_counter
from typing import Callable, List, Tuple

import numpy as np


def sieve_list(n: int) -> List[int]:
    """Sito Eratostenesa na bazie listy bool (indeks = liczba)."""
    if n < 2:
        return []

    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    limit = int(math.isqrt(n))
    for p in range(2, limit + 1):
        if is_prime[p]:
            start = p * p
            step = p
            for m in range(start, n + 1, step):
                is_prime[m] = False

    return [i for i in range(2, n + 1) if is_prime[i]]


def sieve_dict(n: int) -> List[int]:
    """
    Sito z użyciem słownika jako "zbioru").
    Klucze w dict = liczby złożone.
    """
    if n < 2:
        return []

    composites: dict[int, bool] = {}
    limit = int(math.isqrt(n))

    for p in range(2, limit + 1):
        if p not in composites:  # p nie wykreślone -> pierwsza
            start = p * p
            step = p
            for m in range(start, n + 1, step):
                composites[m] = True

    return [i for i in range(2, n + 1) if i not in composites]


def sieve_numpy(n: int) -> np.ndarray:
    """Sito na tablicy numpy (dtype=bool). Zwraca tablicę liczb pierwszych."""
    if n < 2:
        return np.array([], dtype=np.int64)

    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False

    limit = int(math.isqrt(n))
    for p in range(2, limit + 1):
        if is_prime[p]:
            is_prime[p * p : n + 1 : p] = False

    return np.flatnonzero(is_prime).astype(np.int64)


def time_fn(fn: Callable[[int], object], n: int, repeats: int = 3) -> Tuple[float, object]:
    """
    Mierzy czas wykonania funkcji fn(n). Zwraca (najlepszy_czas, wynik).
    Uwaga: wynik jest jest zwracamy z najszybszego pomiaru, żeby nie liczyć drugi raz.
    """
    best_t = float("inf")
    best_result = None

    for _ in range(repeats):
        t0 = perf_counter()
        result = fn(n)
        t1 = perf_counter()
        dt = t1 - t0
        if dt < best_t:
            best_t = dt
            best_result = result

    return best_t, best_result


def parse_n(default_n: int = 1_000_000) -> int:
    """
    Pobiera n z argumentu
    Jeśli brak, używa default_n.
    """
    if len(sys.argv) >= 2:
        try:
            n = int(sys.argv[1])
            return n
        except ValueError:
            pass
    return default_n


def main() -> None:
    n = parse_n(default_n=5_000_000)
    repeats = 3

    print(f"Sito Eratostenesa dla zakresu [2, {n}]")
    print(f"Powtórzenia (bierzemy najlepszy czas): {repeats}\n")

    t_list, primes_list = time_fn(sieve_list, n, repeats=repeats)
    t_dict, primes_dict = time_fn(sieve_dict, n, repeats=repeats)
    t_np, primes_np = time_fn(sieve_numpy, n, repeats=repeats)

    # Ujednolicenie długości i podglądu
    count_list = len(primes_list)
    count_dict = len(primes_dict)
    count_np = int(primes_np.size)

    # Kontrola spójności (na mniejszych n powinno być identycznie)
    ok_counts = (count_list == count_dict == count_np)

    print("WYNIKI:")
    print(f"  LISTA  : {t_list:.6f} s | znaleziono: {count_list}")
    print(f"  SŁOWNIK: {t_dict:.6f} s | znaleziono: {count_dict}")
    print(f"  NUMPY  : {t_np:.6f} s | znaleziono: {count_np}")

    print(f"\nSpójność wyników (liczba liczb pierwszych taka sama): {ok_counts}")

    # Podgląd pierwszych kilkunastu liczb
    preview_k = 20
    preview = primes_np[:preview_k] if count_np >= preview_k else primes_np
    print(f"\nPierwsze {min(preview_k, count_np)} liczb pierwszych:")
    print(preview.tolist())

    # Podgląd ostatnich kilku liczb
    tail_k = 10
    tail = primes_np[-tail_k:] if count_np >= tail_k else primes_np
    print(f"\nOstatnie {min(tail_k, count_np)} liczb pierwszych <= {n}:")
    print(tail.tolist())


if __name__ == "__main__":
    main()