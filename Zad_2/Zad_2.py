from __future__ import annotations

from time import perf_counter
from typing import List, Optional, Set


def digit_histogram(value: int) -> List[int]:
    """Zwraca histogram cyfr liczby value (ile razy występuje 0..9)."""
    histogram = [0] * 10

    if value == 0:
        histogram[0] = 1
        return histogram

    while value > 0:
        histogram[value % 10] += 1
        value //= 10

    return histogram


def max_digit_count_for_armstrong_base10() -> int:
    """
    Wyznacza górną granicę liczby cyfr N, dla której mogą istnieć N-cyfrowe liczby Armstronga
    w systemie dziesiętnym.

    Jeśli maksymalna możliwa suma N * 9^N jest mniejsza niż najmniejsza liczba N-cyfrowa 10^(N-1),
    to dla takiego N nie ma rozwiązań.
    """
    digit_count = 1
    while True:
        lowest_n_digit_number = 0 if digit_count == 1 else 10 ** (digit_count - 1)
        max_possible_sum = digit_count * (9 ** digit_count)

        if max_possible_sum < lowest_n_digit_number:
            return digit_count - 1

        digit_count += 1


def find_armstrong_numbers_with_digit_count(digit_count: int) -> List[int]:
    """
    Szuka liczb Armstronga o dokładnie digit_count cyfrach.

    Zzgodniee z sugestiami z treści zadania):
    - prekomputacja potęg d^N dla d=0..9,
    - generowanie multizbiorów cyfr (histogramów) zamiast wszystkich liczb,
    - sprawdzanie czy suma potęg ma dokładnie N cyfr i ten sam multizbiór cyfr.
    """
    # Zakres liczb o digit_count cyfrach (dla digit_count=1 dopuszczamy 0..9)
    lowest_n_digit_number = 0 if digit_count == 1 else 10 ** (digit_count - 1)
    upper_bound_exclusive = 10 ** digit_count

    # Prekomputacja: digit^digit_count dla digit=0..9
    digit_powers = [digit ** digit_count for digit in range(10)]

    found_numbers: Set[int] = set()
    current_digit_counts = [0] * 10  # histogram cyfr generowanego multizbioru

    def dfs(current_digit: int, remaining_digits: int, current_power_sum: int) -> None:
        """
        Rekurencyjnie rozdziela remaining_digits pomiędzy cyfry current_digit..9.
        Generujemy tylko multizbiory cyfr (odpowiednik cyfr niemalejących).

        Odcięcia:
        - minimalna możliwa suma, gdy resztę wypełnimy current_digit,
        - maksymalna możliwa suma, gdy resztę wypełnimy dziewiątkami.
        """
        min_possible_sum = current_power_sum + remaining_digits * digit_powers[current_digit]
        max_possible_sum = current_power_sum + remaining_digits * digit_powers[9]

        if max_possible_sum < lowest_n_digit_number or min_possible_sum >= upper_bound_exclusive:
            return

        if current_digit == 9:
            current_digit_counts[9] = remaining_digits
            final_sum = current_power_sum + remaining_digits * digit_powers[9]

            if lowest_n_digit_number <= final_sum < upper_bound_exclusive:
                if digit_histogram(final_sum) == current_digit_counts:
                    found_numbers.add(final_sum)

            current_digit_counts[9] = 0
            return

        power_of_current_digit = digit_powers[current_digit]

        # Wybieramy, ile razy wystąpi current_digit: 0..remaining_digits
        for count in range(remaining_digits + 1):
            current_digit_counts[current_digit] = count

            next_power_sum = current_power_sum + count * power_of_current_digit
            next_remaining_digits = remaining_digits - count
            next_digit = current_digit + 1

            # Dodatkowe odcięcie przed zejściem poziom niżej
            next_min = next_power_sum + next_remaining_digits * digit_powers[next_digit]
            next_max = next_power_sum + next_remaining_digits * digit_powers[9]
            if next_max < lowest_n_digit_number or next_min >= upper_bound_exclusive:
                continue

            dfs(next_digit, next_remaining_digits, next_power_sum)

        current_digit_counts[current_digit] = 0

    dfs(0, digit_count, 0)
    return sorted(found_numbers)


def find_armstrong_numbers_up_to(max_digits: Optional[int] = None) -> List[int]:
    """
    Zwraca wszystkie znalezione liczby Armstronga dla długości 1..max_digits.

    Jeśli max_digits=None, program sam wyznacza górną granicę dla base-10
    (na podstawie nierówności N*9^N < 10^(N-1)).
    """
    if max_digits is None:
        max_digits = max_digit_count_for_armstrong_base10()

    results: List[int] = []
    for digit_count in range(1, max_digits + 1):
        results.extend(find_armstrong_numbers_with_digit_count(digit_count))

    return sorted(results)


def main() -> None:
    # Ustawienie:
    # - konkretny limit cyfr (szybciej): np. 10, 12, 15
    # - automatyczna górna granica: ustaw None
    max_digits: Optional[int] = 12

    start = perf_counter()
    armstrong_numbers = find_armstrong_numbers_up_to(max_digits)
    elapsed = perf_counter() - start

    limit_text = "automatyczna granica" if max_digits is None else f"1..{max_digits}"
    print(f"Wyszukiwanie liczba Armstronga dla N = {limit_text}")
    print(f"Znaleziono: {len(armstrong_numbers)}")
    print(f"Czas wykonania: {elapsed:.3f} s\n")

    for number in armstrong_numbers:
        print(number)


if __name__ == "__main__":
    main()