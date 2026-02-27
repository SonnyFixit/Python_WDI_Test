from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class LinearSystemSolution:
    """Wynik klasyfikacji i (opcjonalnie) rozwiązania układu."""
    system_type: str  # 'unique' | 'infinite' | 'inconsistent'
    solution_vector: Optional[np.ndarray]
    coefficient_rank: int
    augmented_rank: int


def load_linear_system_from_file(file_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Wczytuje układ równań liniowych N równań o N niewiadomych z pliku tekstowego.

    Format pliku:
      - 1. linia: liczba równań N
      - kolejne N linii: N współczynników + wyraz wolny

    Przykład:
      3
      1  2  3  7
      -1 2  4  6
      2  1  1  13
    """
    with open(file_path, "r", encoding="utf-8") as file_handle:
        lines = [line.strip() for line in file_handle if line.strip()]

    if not lines:
        raise ValueError("Plik jest pusty albo zawiera wyłącznie puste linie.")

    try:
        number_of_equations = int(lines[0])
    except ValueError as exc:
        raise ValueError("Pierwsza linia musi zawierać liczbę całkowitą N.") from exc

    expected_line_count = number_of_equations + 1
    if len(lines) != expected_line_count:
        raise ValueError(
            f"Błąd formatu: oczekiwano {expected_line_count} linii (N + 1), otrzymano {len(lines)}."
        )

    coefficient_rows: list[list[float]] = []
    constants_values: list[float] = []

    for line_index in range(1, number_of_equations + 1):
        parts = lines[line_index].split()

        if len(parts) != number_of_equations + 1:
            raise ValueError(
                f"Błąd w linii {line_index + 1}: oczekiwano {number_of_equations + 1} liczb, "
                f"otrzymano {len(parts)}."
            )

        try:
            values = [float(value) for value in parts]
        except ValueError as exc:
            raise ValueError(f"Błąd w linii {line_index + 1}: wykryto niepoprawną liczbę.") from exc

        coefficient_rows.append(values[:number_of_equations])
        constants_values.append(values[number_of_equations])

    coefficient_matrix = np.array(coefficient_rows, dtype=float)
    constants_vector = np.array(constants_values, dtype=float)

    # Walidacja zgodności wymiarów (N×N i N)
    if coefficient_matrix.shape != (number_of_equations, number_of_equations):
        raise ValueError("Macierz współczynników ma niepoprawny wymiar. Oczekiwano N×N.")
    if constants_vector.shape != (number_of_equations,):
        raise ValueError("Wektor wyrazów wolnych ma niepoprawny wymiar. Oczekiwano N elementów.")

    return coefficient_matrix, constants_vector


def classify_and_solve_linear_system(
    coefficient_matrix: np.ndarray,
    constants_vector: np.ndarray
) -> LinearSystemSolution:
    """
    Klasyfikuje układ na podstawie rang:
      - inconsistent: rank(A) < rank([A|b])  -> brak rozwiązań
      - unique:       rank(A) = n            -> dokładnie jedno rozwiązanie
      - infinite:     rank(A) = rank([A|b]) < n -> nieskończenie wiele rozwiązań

    Dla układu nieoznaczonego zwracane jest jedno przykładowe rozwiązanie.
    """
    augmented_matrix = np.column_stack((coefficient_matrix, constants_vector))

    coefficient_rank = int(np.linalg.matrix_rank(coefficient_matrix))
    augmented_rank = int(np.linalg.matrix_rank(augmented_matrix))
    number_of_unknowns = int(coefficient_matrix.shape[0])

    if coefficient_rank < augmented_rank:
        return LinearSystemSolution(
            system_type="inconsistent",
            solution_vector=None,
            coefficient_rank=coefficient_rank,
            augmented_rank=augmented_rank
        )

    if coefficient_rank == number_of_unknowns:
        # Układ oznaczony: jedno rozwiązanie
        try:
            solution_vector = np.linalg.solve(coefficient_matrix, constants_vector)
        except np.linalg.LinAlgError:
            # Awaryjnie: w razie problemów numerycznych wracamy do lstsq
            solution_vector, *_ = np.linalg.lstsq(coefficient_matrix, constants_vector, rcond=None)

        return LinearSystemSolution(
            system_type="unique",
            solution_vector=solution_vector,
            coefficient_rank=coefficient_rank,
            augmented_rank=augmented_rank
        )

    # Układ nieoznaczony: zwracamy przykładowe rozwiązanie
    example_solution, *_ = np.linalg.lstsq(coefficient_matrix, constants_vector, rcond=None)
    return LinearSystemSolution(
        system_type="infinite",
        solution_vector=example_solution,
        coefficient_rank=coefficient_rank,
        augmented_rank=augmented_rank
    )

def print_solution_report(
    coefficient_matrix: np.ndarray,
    constants_vector: np.ndarray,
    result: LinearSystemSolution
) -> None:
    """Wypisuje raport."""
    print("=== Raport rozwiązania układu równań liniowych ===")
    print(f"ranga(A)     = {result.coefficient_rank}")
    print(f"ranga([A|b]) = {result.augmented_rank}")
    print()

    if result.system_type == "inconsistent":
        print("Wniosek: układ sprzeczny — brak rozwiązań.")
        return

    if result.system_type == "unique":
        print("Wniosek: układ oznaczony — dokładnie jedno rozwiązanie.")
    else:
        print("Wniosek: układ nieoznaczony — nieskończenie wiele rozwiązań.")
        print("Poniżej jedno przykładowe rozwiązanie:")

    solution_vector = result.solution_vector
    if solution_vector is None:
        print("Błąd: brak wektora rozwiązania (nieoczekiwane dla układu zgodnego).")
        return

    print()
    print("Rozwiązanie:")
    for index, value in enumerate(solution_vector, start=1):
        print(f"  x{index} = {value:.6f}")

def run_from_file(file_path: str) -> None:
    """Uruchamia cały przepływ: wczytanie -> klasyfikacja -> raport."""
    coefficient_matrix, constants_vector = load_linear_system_from_file(file_path)
    result = classify_and_solve_linear_system(coefficient_matrix, constants_vector)
    print_solution_report(coefficient_matrix, constants_vector, result)


# Przykładowe uruchomienie (odkomentuj w razie potrzeby):
run_from_file("dane_zad1.txt")
