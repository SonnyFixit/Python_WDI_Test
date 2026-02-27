import math
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

@dataclass(frozen=True)
class Line:
    """Prosta w postaci: a*x + b*y = c."""
    a: float
    b: float
    c: float
    label: str


_ALLOWED = {
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "round": round,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "exp": math.exp,
}


def safe_eval(expr: str, x: float) -> float:
    """Eval z ograniczonym środowiskiem (tylko x i podstawowe funkcje matematyczne)."""
    env = {"__builtins__": {}}
    loc = dict(_ALLOWED)
    loc["x"] = x
    return float(eval(expr.strip(), env, loc))


def linear_from_y(expr: str) -> Tuple[float, float]:
    """Z wyrażenia y(x) wyznacza a i b dla y = a*x + b (sprawdza liniowość)."""
    y0 = safe_eval(expr, 0.0)
    y1 = safe_eval(expr, 1.0)
    a = y1 - y0
    b = y0

    y2 = safe_eval(expr, 2.0)
    if not math.isclose(y2, 2.0 * a + b, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("Równanie w postaci y=... nie wygląda na liniowe y = a*x + b.")
    return a, b


def parse_lhs(lhs: str) -> Tuple[float, float, float]:
    """
    Parsuje lewą stronę do postaci: a*x + b*y + d
    Akceptuje np.: '2x-3y', '-x+y', '2*x-3*y+1'
    """
    s = lhs.replace(" ", "").replace("*", "").replace("−", "-")

    a = b = d = 0.0
    i = 0

    def read_number(pos: int) -> Tuple[Optional[float], int]:
        j = pos
        has_digit = False
        while j < len(s) and (s[j].isdigit() or s[j] == "."):
            has_digit = True
            j += 1
        if not has_digit:
            return None, pos
        return float(s[pos:j]), j

    while i < len(s):
        sign = 1.0
        if s[i] == "+":
            i += 1
        elif s[i] == "-":
            sign = -1.0
            i += 1

        num, j = read_number(i)
        i = j
        coeff = 1.0 if num is None else num

        if i < len(s) and s[i] in ("x", "y"):
            var = s[i]
            i += 1
            if var == "x":
                a += sign * coeff
            else:
                b += sign * coeff
        else:
            if num is None:
                raise ValueError(f"Nie potrafię sparsować fragmentu: '{s[i:]}'")
            d += sign * coeff

    return a, b, d


def parse_equation(eq: str) -> Line:
    """
    Obsługa:
    - y = 2*x + 1  (lub samo: 2*x+1)
    - 2x - 3y = 7
    Zwraca prostą w postaci a*x + b*y = c.
    """
    raw = eq.strip()
    if not raw:
        raise ValueError("Puste równanie.")

    s = raw.replace(" ", "").replace("−", "-")

    if "=" not in s:
        a, b0 = linear_from_y(s)
        return Line(a=a, b=-1.0, c=-b0, label=f"y={raw}")

    left, right = s.split("=", 1)

    if left.lower() == "y":
        a, b0 = linear_from_y(right)
        return Line(a=a, b=-1.0, c=-b0, label=raw)

    # ax + by = c (po prawej liczba lub proste wyrażenie liczbowe)
    try:
        c = float(right)
    except ValueError:
        c = safe_eval(right, x=0.0)

    a, b, d = parse_lhs(left)
    return Line(a=a, b=b, c=c - d, label=raw)


def solve_system(l1: Line, l2: Line) -> Tuple[str, Optional[Tuple[float, float]]]:
    """Zwraca status: 'unique' / 'none' / 'infinite' oraz punkt przecięcia (jeśli jest)."""
    det = l1.a * l2.b - l2.a * l1.b

    if math.isclose(det, 0.0, abs_tol=1e-12):
        # Te same proste, jeśli (a,b,c) są proporcjonalne
        same = (
            math.isclose(l1.a * l2.b, l2.a * l1.b, abs_tol=1e-12)
            and math.isclose(l1.a * l2.c, l2.a * l1.c, abs_tol=1e-12)
            and math.isclose(l1.b * l2.c, l2.b * l1.c, abs_tol=1e-12)
        )
        return ("infinite", None) if same else ("none", None)

    x = (l1.c * l2.b - l2.c * l1.b) / det
    y = (l1.a * l2.c - l2.a * l1.c) / det
    return "unique", (x, y)


def plot_system(l1: Line, l2: Line) -> None:
    status, sol = solve_system(l1, l2)

    if sol:
        x0, y0 = sol
        xmin, xmax = x0 - 10, x0 + 10
        ymin, ymax = y0 - 10, y0 + 10
    else:
        xmin, xmax = -10, 10
        ymin, ymax = -10, 10

    xs = np.linspace(xmin, xmax, 600)

    def draw(line: Line) -> None:
        # a*x + b*y = c
        if not math.isclose(line.b, 0.0, abs_tol=1e-12):
            ys = (line.c - line.a * xs) / line.b
            plt.plot(xs, ys, label=line.label)
        else:
            # pionowa: a*x = c
            if not math.isclose(line.a, 0.0, abs_tol=1e-12):
                plt.axvline(line.c / line.a, label=line.label)

    draw(l1)
    draw(l2)

    if status == "unique" and sol:
        x0, y0 = sol
        plt.scatter([x0], [y0])
        plt.annotate(f"({x0:.3f}, {y0:.3f})", (x0, y0), textcoords="offset points", xytext=(8, 8))
        print(f"Rozwiązanie: x={x0}, y={y0}")
        plt.title(f"Jedno rozwiązanie: x={x0:.6g}, y={y0:.6g}")
    elif status == "none":
        print("Brak rozwiązań (proste równoległe).")
        plt.title("Brak rozwiązań (proste równoległe)")
    else:
        print("Nieskończenie wiele rozwiązań (te same proste).")
        plt.title("Nieskończenie wiele rozwiązań (te same proste)")

    plt.axhline(0)
    plt.axvline(0)
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.grid(True)
    plt.legend()
    plt.show()


def run_plot_tests() -> None:
    # Każdy test: (opis, równanie 1, równanie 2, oczekiwany status, oczekiwane (x,y) lub None)
    tests = [
        (
            "Jedno rozwiązanie (przecięcie)",
            "y = 2*x + 1",
            "2x - 3y = 7",
            "unique",
            (-2.5, -4.0),
        ),
        (
            "Brak rozwiązań (równoległe, różne)",
            "y = 2*x + 1",
            "y = 2*x - 3",
            "none",
            None,
        ),
        (
            "Nieskończenie wiele rozwiązań (te same proste)",
            "2x - 3y = 7",
            "4x - 6y = 14",
            "infinite",
            None,
        ),
        (
            "Przypadek pionowej prostej",
            "1x + 0y = 2",
            "y = -x + 1",
            "unique",
            (2.0, -1.0),
        ),
    ]

    for idx, (title, eq1, eq2, expected_status, expected_point) in enumerate(tests, start=1):
        print("\n" + "=" * 60)
        print(f"TEST {idx}: {title}")
        print(f"  eq1: {eq1}")
        print(f"  eq2: {eq2}")

        l1 = parse_equation(eq1)
        l2 = parse_equation(eq2)

        status, sol = solve_system(l1, l2)
        print(f"  status: {status}, sol: {sol}")

        assert status == expected_status, f"Status niezgodny: {status} != {expected_status}"

        if expected_point is not None:
            assert sol is not None, "Oczekiwano punktu przecięcia, ale go nie ma."
            x, y = sol
            ex, ey = expected_point
            assert math.isclose(x, ex, rel_tol=1e-9, abs_tol=1e-9), f"x niezgodne: {x} != {ex}"
            assert math.isclose(y, ey, rel_tol=1e-9, abs_tol=1e-9), f"y niezgodne: {y} != {ey}"
            print("  OK: punkt przecięcia zgodny z oczekiwaniami.")
        else:
            print("  OK: typ rozwiązania zgodny z oczekiwaniami.")

        plot_system(l1, l2)


if __name__ == "__main__":
    run_plot_tests()