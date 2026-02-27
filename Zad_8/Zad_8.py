import random
from copy import deepcopy
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt

Grid = List[List[int]]
ALL_MASK = (1 << 9) - 1  # kandydaci 1..9


def bit(d: int) -> int:
    return 1 << (d - 1)


def box_index(r: int, c: int) -> int:
    return (r // 3) * 3 + (c // 3)


def build_masks(grid: Grid) -> Tuple[List[int], List[int], List[int]]:
    """Buduje maski zajętych cyfr dla wierszy, kolumn i boksów."""
    row = [0] * 9
    col = [0] * 9
    box = [0] * 9
    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            if v:
                m = bit(v)
                b = box_index(r, c)
                row[r] |= m
                col[c] |= m
                box[b] |= m
    return row, col, box


def candidates_mask(row: List[int], col: List[int], box: List[int], r: int, c: int) -> int:
    """Zwraca maskę kandydatów dla pustej komórki."""
    used = row[r] | col[c] | box[box_index(r, c)]
    return ALL_MASK & ~used


def digits_from_mask(mask: int, rng: Optional[random.Random] = None) -> List[int]:
    """Zamienia maskę na listę cyfr; opcjonalnie losuje kolejność."""
    ds = [d for d in range(1, 10) if mask & bit(d)]
    if rng is not None:
        rng.shuffle(ds)
    return ds


def find_mrv_cell(grid: Grid, row: List[int], col: List[int], box: List[int]) -> Optional[Tuple[int, int, int]]:
    """
    Wybiera pustą komórkę z najmniejszą liczbą kandydatów (MRV).
    Zwraca (r, c, maska_kandydatów) albo None, gdy plansza pełna.
    """
    best = None
    best_cnt = 10
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                m = candidates_mask(row, col, box, r, c)
                cnt = m.bit_count()
                if cnt == 0:
                    return (r, c, 0)
                if cnt < best_cnt:
                    best_cnt = cnt
                    best = (r, c, m)
                    if best_cnt == 1:
                        return best
    return best


def count_solutions(grid: Grid, limit: int = 2) -> int:
    """Liczy rozwiązania, ale przerywa po osiągnięciu limitu."""
    row, col, box = build_masks(grid)

    def backtrack() -> int:
        cell = find_mrv_cell(grid, row, col, box)
        if cell is None:
            return 1
        r, c, m = cell
        if m == 0:
            return 0

        total = 0
        b = box_index(r, c)
        for d in digits_from_mask(m): 
            md = bit(d)
            grid[r][c] = d
            row[r] |= md
            col[c] |= md
            box[b] |= md

            total += backtrack()
            # cofanie
            box[b] &= ~md
            col[c] &= ~md
            row[r] &= ~md
            grid[r][c] = 0

            if total >= limit:
                return total
        return total

    return backtrack()


def solve_one(grid: Grid, rng: random.Random) -> bool:
    """Wypełnia planszę jednym rozwiązaniem (backtracking + MRV)."""
    row, col, box = build_masks(grid)

    def backtrack() -> bool:
        cell = find_mrv_cell(grid, row, col, box)
        if cell is None:
            return True
        r, c, m = cell
        if m == 0:
            return False

        b = box_index(r, c)
        for d in digits_from_mask(m, rng): 
            md = bit(d)
            grid[r][c] = d
            row[r] |= md
            col[c] |= md
            box[b] |= md

            if backtrack():
                return True

            box[b] &= ~md
            col[c] &= ~md
            row[r] &= ~md
            grid[r][c] = 0

        return False

    return backtrack()


def generate_full_grid(seed: Optional[int] = None) -> Grid:
    """Generuje pełną, poprawną planszę sudoku."""
    rng = random.Random(seed)
    grid = [[0] * 9 for _ in range(9)]
    if not solve_one(grid, rng):
        raise RuntimeError("Nie udało się wygenerować pełnej planszy.")
    return grid


def remove_cells_unique(full: Grid, rng: random.Random, symmetry: bool = True) -> Grid:
    """
    Usuwa pola zachłannie, ale tylko wtedy, gdy sudoku nadal ma dokładnie jedno rozwiązanie.
    symmetry=True usuwa symetryczne pary.
    """
    puzzle = deepcopy(full)
    cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(cells)

    def paired(r: int, c: int) -> List[Tuple[int, int]]:
        if not symmetry:
            return [(r, c)]
        r2, c2 = 8 - r, 8 - c
        return [(r, c)] if (r, c) == (r2, c2) else [(r, c), (r2, c2)]

    for r, c in cells:
        targets = paired(r, c)
        if all(puzzle[rr][cc] == 0 for rr, cc in targets):
            continue

        backup = [(rr, cc, puzzle[rr][cc]) for rr, cc in targets]
        for rr, cc, _ in backup:
            puzzle[rr][cc] = 0

        tmp = deepcopy(puzzle)
        if count_solutions(tmp, limit=2) != 1:
            for rr, cc, v in backup:
                puzzle[rr][cc] = v

    return puzzle


def generate_puzzle(attempts: int = 5, symmetry: bool = True, seed: Optional[int] = None) -> Tuple[Grid, Grid]:
    """Kilka prób, wybór wariantu z największą liczbą pustych pól."""
    rng = random.Random(seed)

    best_puzzle: Optional[Grid] = None
    best_solution: Optional[Grid] = None
    best_zeros = -1

    for _ in range(attempts):
        solution = generate_full_grid(seed=rng.randrange(10**9))
        puzzle = remove_cells_unique(solution, rng=rng, symmetry=symmetry)

        zeros = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
        if zeros > best_zeros:
            best_zeros = zeros
            best_puzzle = puzzle
            best_solution = solution

    assert best_puzzle is not None and best_solution is not None
    return best_puzzle, best_solution


def print_grid_ascii(grid: Grid) -> None:
    """Podstawwy wydruk sudoku w konsoli."""
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row.append("|")
            row.append(str(grid[r][c]) if grid[r][c] else ".")
        print(" ".join(row))


def plot_sudoku(grid: Grid, title: str, givens: Optional[List[List[bool]]] = None) -> None:
    """Wykres sudoku w matplotlib"""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(title)

    for i in range(10):
        lw = 2.5 if i % 3 == 0 else 1.0
        ax.plot([0, 9], [i, i], linewidth=lw)
        ax.plot([i, i], [0, 9], linewidth=lw)

    ax.set_xlim(0, 9)
    ax.set_ylim(0, 9)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")

    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            if v:
                x = c + 0.5
                y = 8.5 - r
                bold = givens is not None and givens[r][c]
                ax.text(x, y, str(v), ha="center", va="center", fontsize=16,
                        fontweight="bold" if bold else "normal")

    plt.show()


if __name__ == "__main__":
    ATTEMPTS = 6
    SYMMETRY = True
    SEED = None
    SHOW_SOLUTION = True

    puzzle, solution = generate_puzzle(attempts=ATTEMPTS, symmetry=SYMMETRY, seed=SEED)

    givens = [[puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
    blanks = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
    clues = 81 - blanks

    print(f"Puste pola: {blanks} | Podane cyfry: {clues}\n")
    print_grid_ascii(puzzle)

    plot_sudoku(puzzle, title=f"Sudoku (podane={clues}, puste={blanks})", givens=givens)

    if SHOW_SOLUTION:
        plot_sudoku(solution, title="Rozwiązanie")