import re
import argparse
from collections import Counter
from pathlib import Path

WORD_PATTERN = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+")

def get_script_directory() -> Path:
    try:
        return Path(__file__).resolve().parent
    except NameError:
        return Path.cwd()


def read_text_file(file_path: Path) -> str:
    # UTF-8 + fallback, gdyby plik był w Windows-1250
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="cp1250")


def extract_words(text: str) -> list[str]:
    # Wyciągamy słowa i sprowadzamy do małych liter, żeby nie rozróżniać wielkości liter
    return [word.lower() for word in WORD_PATTERN.findall(text)]


def get_top_longest_words(words: list[str], top_k: int = 20) -> list[tuple[str, int, int]]:
    # Zliczamy wystąpienia każdego słowa
    word_counts = Counter(words)

    # Bierzemy unikalne słowa i sortujemy: najpierw po długości malejąco, potem alfabetycznie
    unique_words = list(word_counts.keys())
    unique_words.sort(key=lambda w: (-len(w), w))

    selected = unique_words[:top_k]
    return [(w, len(w), word_counts[w]) for w in selected]


def select_input_file(script_dir: Path, provided_path: str | None) -> Path:
    """
    Wybór pliku:
    1) jeśli podano --file i to nie jest kernel*.json -> użyj go
    2) jeśli w folderze jest Pan_Tadeusz.txt -> użyj
    3) jeśli w folderze jest dokładnie 1 plik .txt -> użyj
    4) inaczej: błąd i lista plików .txt
    """
    # 1) jeśli użytkownik podał --file
    if provided_path:
        candidate = Path(provided_path)

        # Filtr na przypadek, gdyby ktoś przekazał plik kernela z Jupytera
        is_kernel_json = candidate.suffix.lower() == ".json" and "kernel" in candidate.name.lower()
        if not is_kernel_json:
            # Jeśli ścieżka względna -> licz względem folderu skryptu
            if not candidate.is_absolute():
                candidate = script_dir / candidate
            return candidate

    # 2) standardowa nazwa
    default_candidate = script_dir / "Pan_Tadeusz.txt"
    if default_candidate.exists():
        return default_candidate

    # 3) jeśli jest tylko jeden txt w folderze
    txt_files = sorted(script_dir.glob("*.txt"))
    if len(txt_files) == 1:
        return txt_files[0]

    # 4) nie znaleziono
    raise FileNotFoundError(
        "Nie znaleziono pliku wejściowego. Umieść 'Pan_Tadeusz.txt' obok skryptu "
        "albo podaj --file <nazwa_pliku.txt>."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Wypisz 20 najdłuższych słów z pliku tekstowego.")
    parser.add_argument(
        "--file",
        default=None,
        help="Nazwa/ścieżka do pliku TXT. Jeśli względna, liczona względem folderu skryptu.",
    )
    parser.add_argument(
        "--top", "-k",
        type=int,
        default=20,
        help="Ile najdłuższych słów wypisać (domyślnie: 20).",
    )

    args, _unknown = parser.parse_known_args()

    script_dir = get_script_directory()

    try:
        input_path = select_input_file(script_dir, args.file)
    except FileNotFoundError as exc:
        print(exc)
        txt_files = sorted(p.name for p in script_dir.glob("*.txt"))
        if txt_files:
            print("\nPliki .txt w folderze skryptu:")
            for name in txt_files:
                print(f" - {name}")
        return

    if not input_path.exists():
        print(f"Nie znaleziono pliku: {input_path}")
        return

    text = read_text_file(input_path)
    words = extract_words(text)
    results = get_top_longest_words(words, top_k=args.top)

    print(f"Folder skryptu: {script_dir}")
    print(f"Plik: {input_path.name}")
    print(f"Liczba słów (tokenów): {len(words)}")
    print(f"Unikalnych słów: {len(set(words))}\n")

    print(f"{args.top} najdłuższych słów:")
    for index, (word, length, occurrences) in enumerate(results, start=1):
        print(f"{index:2d}. {word}  (dł={length}, wystąpienia={occurrences})")


if __name__ == "__main__":
    main()