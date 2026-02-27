from pathlib import Path

def get_script_directory() -> Path:
    """Zwraca folder, w którym znajduje się uruchomiony skrypt .py."""
    return Path(__file__).resolve().parent


def parse_key_digits(key: str) -> list[int]:
    """
    Zamienia klucz (ciąg cyfr) na listę cyfr klucza.
    Przykład: "31206" -> [3, 1, 2, 0, 6]
    """
    key = key.strip()
    if not key or not key.isdigit():
        raise ValueError("Klucz musi być niepustym ciągiem cyfr, np. 31206.")
    return [int(ch) for ch in key]


def shift_letter(letter: str, shift: int, decrypt: bool) -> str:
    """
    Przesuwa jedną literę alfabetu łacińskiego o podaną wartość.
    - Obsługiwane są tylko litery A–Z oraz a–z.
    - Pozostałe znaki (spacje, cyfry, interpunkcja, polskie litery) są zwracane bez zmian.
    """
    if "A" <= letter <= "Z":
        base = ord("A")
        position = ord(letter) - base
        position = (position - shift) % 26 if decrypt else (position + shift) % 26
        return chr(base + position)

    if "a" <= letter <= "z":
        base = ord("a")
        position = ord(letter) - base
        position = (position - shift) % 26 if decrypt else (position + shift) % 26
        return chr(base + position)

    return letter


def gronsfeld_cipher(text: str, key: str, decrypt: bool = False) -> str:
    """
    Szyfr Gronsfelda (modyfikacja Cezara) dla tekstu:
    - kolejne litery przesuwamy o kolejne cyfry klucza,
    - klucz powtarza się cyklicznie,
    - znaki nieliterowe nie są szyfrowane i nie zużywają cyfr klucza.
    """
    key_digits = parse_key_digits(key)
    key_length = len(key_digits)
    key_index = 0  # indeks aktualnie używanej cyfry klucza

    output_chars: list[str] = []

    for ch in text:
        # Zużywamy klucz tylko dla liter A–Z/a–z
        if ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            shift = key_digits[key_index % key_length]
            output_chars.append(shift_letter(ch, shift, decrypt))
            key_index += 1
        else:
            # Inne znaki przepisujemy bez zmian
            output_chars.append(ch)

    return "".join(output_chars)


def encrypt_text(text: str, key: str) -> str:
    """Szyfruje tekst kluczem Gronsfelda."""
    return gronsfeld_cipher(text, key, decrypt=False)


def decrypt_text(text: str, key: str) -> str:
    """Odszyfrowuje tekst zaszyfrowany Gronsfeldem."""
    return gronsfeld_cipher(text, key, decrypt=True)


def encrypt_file(input_name: str, output_name: str, key: str) -> None:
    """
    Wczytuje plik tekstowy z folderu skryptu, szyfruje i zapisuje wynik do innego pliku.
    """
    script_dir = get_script_directory()
    input_path = script_dir / input_name
    output_path = script_dir / output_name

    text = input_path.read_text(encoding="utf-8")
    encrypted = encrypt_text(text, key)
    output_path.write_text(encrypted, encoding="utf-8")


def decrypt_file(input_name: str, output_name: str, key: str) -> None:
    """
    Wczytuje plik zaszyfrowany z folderu skryptu, odszyfrowuje i zapisuje wynik do innego pliku.
    """
    script_dir = get_script_directory()
    input_path = script_dir / input_name
    output_path = script_dir / output_name

    text = input_path.read_text(encoding="utf-8")
    decrypted = decrypt_text(text, key)
    output_path.write_text(decrypted, encoding="utf-8")


def read_file_text(file_name: str) -> str:
    """Wczytuje plik z folderu skryptu i zwraca jego treść jako tekst."""
    path = get_script_directory() / file_name
    return path.read_text(encoding="utf-8")


def print_file_section(title: str, file_name: str, content: str) -> None:
    """ypisuje sekcję z nazwą pliku i jego treścią w czytelnym formacie."""
    print(f"\n--- {title} ({file_name}) ---")
    print(content)


def self_test() -> None:
    """
    Ttesty poprawności:
    - test zgodny z przykładem z zadania,
    - test z tekstem mieszanym (wielkość liter, znaki nieliterowe).
    """
    # Test 1: przykład z treści zadania
    key = "31206"
    plain = "PROGRAMOWANIE"
    cipher = encrypt_text(plain, key)
    back = decrypt_text(cipher, key)

    print("TEST 1")
    print("plain :", plain)
    print("cipher:", cipher)
    print("back  :", back)
    assert cipher == "SSQGXDNQWGQJG"
    assert back == plain

    # Test 2: inny tekst + znaki nieliterowe
    key2 = "901"
    plain2 = "Ala ma kota! 123. XYZ xyz"
    cipher2 = encrypt_text(plain2, key2)
    back2 = decrypt_text(cipher2, key2)

    print("\nTEST 2")
    print("plain :", plain2)
    print("cipher:", cipher2)
    print("back  :", back2)
    assert back2 == plain2

if __name__ == "__main__":
    self_test()

    # Test na plikach w tym samym folderze co skrypt:
    KEY = "31206"
    INPUT_FILE = "jawny.txt"
    ENCRYPTED_FILE = "szyfr.txt"
    DECRYPTED_FILE = "odszyfrowany.txt"

    encrypt_file(INPUT_FILE, ENCRYPTED_FILE, KEY)
    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE, KEY)

    # Wypisanie treści plików jako potwierdzenie działania
    plain_text = read_file_text(INPUT_FILE)
    encrypted_text = read_file_text(ENCRYPTED_FILE)
    decrypted_text = read_file_text(DECRYPTED_FILE)

    print_file_section("Tekst jawny", INPUT_FILE, plain_text)
    print_file_section("Tekst zaszyfrowany", ENCRYPTED_FILE, encrypted_text)
    print_file_section("Tekst odszyfrowany", DECRYPTED_FILE, decrypted_text)

    # Sprawdzenieczy odszyfrowany tekst jest identyczny z jawnym
    is_same = plain_text == decrypted_text
    print(f"\nPorównanie: odszyfrowany tekst jest identyczny z jawnym: {is_same}")
    print(f"Zrobione: {INPUT_FILE} -> {ENCRYPTED_FILE} -> {DECRYPTED_FILE}")