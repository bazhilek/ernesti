import re
import json
import unicodedata
import xml.etree.ElementTree as ET

def remove_empty_lines(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Usunięcie pustych linii
    cleaned_lines = [line for line in lines if line.strip()]

    with open(input_file, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)


def merge_lines_1(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    skip_next = False

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        line = lines[i].strip()

        # Jeśli linia kończy się na "-", sprawdzamy następną
        if line.endswith('-') and i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            if next_line and next_line[0].isupper():  # Sprawdza, czy zaczyna się od wielkiej litery
                line = line + next_line  # Doklejamy, ale zostawiamy "-"
            else:
                line = line[:-1] + next_line  # Usuwamy "-" i doklejamy tekst

            skip_next = True  # Pomijamy następną linię, bo już ją użyliśmy

        processed_lines.append(line)

    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_lines) + '\n')


def merge_lines_2(input_file):
    """
    Wczytuje plik wejściowy, iteruje po liniach i:
    - pomija linie zawierające "###",
    - dokleja linie zaczynające się małą literą do poprzedniej, niezależnie czy zawierają "/".
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    merged_lines = []
    for i in range(len(lines)):
        line = lines[i].strip()

        # Pomijanie linii zawierających "###"
        if '###' in line:
            merged_lines.append(line)
            continue

        # Sprawdzenie, czy linia zaczyna się od małej litery albo nie zawiera "/"
        if line and line[0].islower() or "/" not in line:
            if merged_lines:
                merged_lines[-1] += ' ' + line
            else:
                merged_lines.append(line)
        else:
            merged_lines.append(line)

    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_lines))


def extract_signatures(file_path, json_path):
    """
    Analizuje plik tekstowy i usuwa linie zgodnie z podanymi kryteriami.

    :param file_path: Ścieżka do pliku tekstowego
    :param json_path: Ścieżka do pliku JSON, gdzie zapisywane będą usunięte linie
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    pages = {}
    filtered_lines = []
    lines_to_remove = set()  # Przechowuje linie do usunięcia

    i = 0
    while i < len(lines):
        if lines[i].startswith("###"):
            prev_lines = lines[max(0, i - 2):i]
            for prev_line in prev_lines:
                if re.match(r"^[A-Z](?: [ijv]+)?$", prev_line):  # Obsługuje "A", "A ij", "B v" itd.
                    pages[int(lines[i].strip().split()[1]) - 1] = prev_line.strip()
                    lines_to_remove.add(prev_line)  # Oznacz linię do usunięcia
                    break  # Znaleziono pasującą linię, przerywamy sprawdzanie

            filtered_lines.append(lines[i])  # "###" zawsze zostaje w pliku
        else:
            filtered_lines.append(lines[i])

        i += 1

    # Tworzymy nową listę bez usuniętych linii
    filtered_lines = [line for line in filtered_lines if line not in lines_to_remove]

    # Zapisujemy przefiltrowane linie do pliku tekstowego
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

    # Zapisujemy zebrane strony do JSON
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(pages, json_file, ensure_ascii=False, indent=4)


def normalize(text):
    """Usuwa diakrytyki i konwertuje na małe litery dla porównania."""
    return ''.join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).lower()


def extract_custos(file_path, json_path):
    """
    Analizuje plik tekstowy i usuwa linie zgodnie z podanymi kryteriami.

    :param file_path: Ścieżka do pliku tekstowego
    :param json_path: Ścieżka do pliku JSON, gdzie zapisywane będą usunięte linie
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    pages = {}
    filtered_lines = []
    lines_to_remove = set()  # Przechowuje linie do usunięcia

    for i in range(len(lines) - 1):  # -1, żeby mieć pewność, że mamy kolejną linię do sprawdzenia
        if lines[i].startswith("###") and i > 0:
            prev_line = lines[i - 1].strip()
            next_line = lines[i + 1].strip()

            # Usuwamy ewentualny '/' na końcu
            # word_fragment = prev_line.rstrip('/-')
            word_fragment = prev_line[:2]

            # Normalizujemy oba fragmenty do porównania
            norm_fragment = normalize(word_fragment)
            norm_next_line = normalize(next_line)

            # Sprawdzamy, czy następna linia zaczyna się od tego fragmentu
            if norm_next_line.startswith(norm_fragment):
                page_number = int(lines[i].split()[1]) - 1  # Pobranie numeru strony i odjęcie 1
                pages[page_number] = prev_line
                lines_to_remove.add(prev_line)  # Oznaczamy linię do usunięcia

        filtered_lines.append(lines[i])

    # Tworzymy nową listę bez usuniętych linii
    filtered_lines = [line for line in filtered_lines if line.strip() not in lines_to_remove]

    # Zapisujemy przefiltrowane linie do pliku tekstowego
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

    # Zapisujemy zebrane custos do JSON
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(pages, json_file, ensure_ascii=False, indent=4)


def remove_parens(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        linie = f.readlines()

    for i, linia in enumerate(linie):
        if "(" in linia:
            print("\n--- Znaleziono '(' w linii", i + 1, "---")
            start = i
            end = min(len(linie), i + 3)

            # Pobranie fragmentu do edycji
            fragment = linie[start:end]
            for j, l in enumerate(fragment, start):
                print(l.strip())

            # Pobranie edytowanych linii od użytkownika
            print("\nWpisz poprawione linie i naciśnij ENTER dwa razy (lub wpisz '.' aby pominąć):")
            nowe_linie = []
            while True:
                nowa_linia = input()
                if nowa_linia == "" and nowe_linie:
                    break
                if nowa_linia == ".":
                    nowe_linie = fragment  # Nie zmieniaj nic
                    break
                nowe_linie.append(nowa_linia + "\n")

            # Aktualizacja pliku
            linie[start:end] = nowe_linie
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(linie)

            print("Zapisano zmiany!\n")


def remove_braces(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Przetwarzanie dla linii z "}" i następnej linii
        if "}" in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()

            # Podział linii na część przed i po ukośniku
            line_parts = line.split("/")
            next_parts = next_line.split("/")

            # Zapewnienie, że obie części istnieją
            line_part1 = line_parts[0].strip()
            line_part2 = line_parts[1].strip() if len(line_parts) > 1 else ""
            next_part1 = next_parts[0].strip()
            next_part2 = next_parts[1].strip() if len(next_parts) > 1 else ""

            # Usunięcie klamerek
            line_part2 = line_part2.replace("}", "").strip()
            next_part2 = next_part2.replace("{", "").strip()

            # Łączenie pierwszych części średnikiem
            new_part1 = f"{line_part1}; {next_part1}"

            # Sprawdzenie łączenia drugiej części
            if "-" in line_part2:
                line_part2 = line_part2.replace("-", "") + next_part2
            else:
                line_part2 = f"{line_part2} {next_part2}".strip()

            result.append(f"{new_part1}/ {line_part2}".strip())
            i += 1  # Pominiecie następnej linii, bo już została przetworzona
        else:
            result.append(line)

        i += 1

        # Zapis przetworzonych danych do pliku
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(result) + "\n")

    return result


def txt_to_tei(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tei_entries = []

    for line in lines:
        line = line.strip()

        if line.startswith("###"):
            page_number = line[3:].strip().lstrip("0")
            tei_entries.append(f'<pb n="{page_number}"/>')
        elif "/" in line:
            headword, translation = line.split("/", 1)
            headword = headword.strip()
            translation = translation.strip()

            entry = f'''
            <entry>
                <form type="lemma">
                    <orth>{headword}</orth>
                </form>
                <sense>
                    <cit type="translationEquivalent" xml:lang="ger">
                        <form>
                            <orth>{translation}</orth>
                        </form>
                    </cit>
                </sense>
            </entry>
            '''
            tei_entries.append(entry.strip())

    tei_content = """
    <TEI>
    <teiHeader/>
        <text>
            <body>
    """ + "\n".join(tei_entries) + """
            </body>
        </text>
    </TEI>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tei_content.strip())

    return output_file


def custos_from_json(tei_file, json_file):
    # Wczytanie TEI XML
    tree = ET.parse(tei_file)
    root = tree.getroot()

    # Wczytanie JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Przechodzenie po kluczach JSON
    for page_number, fw_text in data.items():
        target_page = str(int(page_number) + 1)  # Klucz +1 jako string

        # Znalezienie odpowiedniego <pb>
        for parent in root.iter():
            for i, pb in enumerate(list(parent)):
                if pb.tag == "pb" and pb.attrib.get("n") == target_page:
                    # Tworzenie nowego elementu <fw>
                    fw_element = ET.Element("fw", type="custos")
                    fw_element.text = fw_text

                    # Wstawienie <fw> bezpośrednio przed <pb>
                    parent.insert(i, fw_element)
                    break

    # Zapis zmodyfikowanego TEI do pliku
    tree.write(tei_file, encoding="utf-8", xml_declaration=True)

    return tei_file


def signatures_from_json(tei_file, json_file):
    # Wczytanie TEI XML
    tree = ET.parse(tei_file)
    root = tree.getroot()

    # Wczytanie JSON
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Przechodzenie po kluczach JSON
    for page_number, fw_text in data.items():
        target_page = str(int(page_number) + 1)  # Klucz +1 jako string

        # Znalezienie odpowiedniego <pb>
        for parent in root.iter():
            for i, pb in enumerate(list(parent)):
                if pb.tag == "pb" and pb.attrib.get("n") == target_page:
                    # Tworzenie nowego elementu <fw>
                    fw_element = ET.Element("fw", type="signature")
                    fw_element.text = fw_text

                    # Wstawienie <fw> bezpośrednio przed <pb>
                    parent.insert(i, fw_element)
                    break

    # Zapis zmodyfikowanego TEI do pliku
    tree.write(tei_file, encoding="utf-8", xml_declaration=True)

    return tei_file




# remove_empty_lines('Ern_4_sk 113-162.txt')
# extract_signatures('Ern_4_sk 113-162.txt', 'sign3.json')
# extract_custos('Ern_4_sk 113-162.txt', 'custos3.json')
# remove_parens('Ern_4_sk 113-162.txt')
# merge_lines_1('Ern_4_sk 113-162.txt')
# merge_lines_2('Ern_4_sk 113-162.txt')
# remove_braces('Ern_4_sk 113-162.txt')
# txt_to_tei('Ern_3_sk 63-112.txt', '2.xml')
# signatures_from_json('2.xml', 'sign2.json')
# custos_from_json('2.xml', 'custos2.json')
