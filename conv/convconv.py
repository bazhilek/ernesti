import re
import json
import unicodedata
import xml.etree.ElementTree as ET
from ernesti.dict.ernesti2tei import remove_empty_lines, extract_custos, extract_signatures, normalize, merge_lines_1, merge_lines_2, custos_from_json, signatures_from_json
from xml.sax.saxutils import escape

speakers = ["Bogumił.", "Piotr", "Bog.", "Ian.", "Piotr.", "Bog/", "Piotr/", "Iá.", "Ierzy.", "Mich.", "Iák.", "Krysztof.", "Krysz.", "Ierzy", "Tomasz.", "Tom.", "Mich/", "Iak."]

def convert_to_tei(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output = ['<TEI xmlns="http://www.tei-c.org/ns/1.0">', '<text>', '<body>']
    current_speaker = None
    inside_sp = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Znacznik strony
        if line.startswith("###"):
            pb_number = re.sub(r"[^\d]", "", line)
            output.append(f'    <pb n="{pb_number}"/>')
            continue

        # Nowy mówca
        matched_speaker = next(
            (s for s in speakers if re.match(rf'^{re.escape(s)}(\s|$)', line)), None)
        if matched_speaker:
            if inside_sp:
                output.append('  </sp>')
            speaker_token = next(s for s in speakers if line.startswith(s))
            output.append('  <sp>')
            output.append(f'    <speaker>{escape(speaker_token)}</speaker>')
            inside_sp = True
            line = line[len(speaker_token):].strip()

            # Jeśli jest coś po nazwie mówcy
            if '/' in line:
                pl, de = map(str.strip, line.split('/', 1))
                output.append(f'    <seg xml:lang="pl">{escape(pl)}</seg>')
                output.append(f'    <seg xml:lang="de">{escape(de)}</seg>')
            elif line:
                output.append(f'    <seg xml:lang="pl">{escape(line)}</seg>')
            continue

        # Wewnątrz mowy: kontynuacja
        if inside_sp:
            if '/' in line:
                pl, sep, de = line.partition('/')
                pl = pl.strip() + sep  # Dodajemy '/' z powrotem na końcu segmentu polskiego
                de = de.strip()
                output.append(f'    <seg xml:lang="pl">{escape(pl)}</seg>')
                output.append(f'    <seg xml:lang="de">{escape(de)}</seg>')
            else:
                output.append(f'    <seg xml:lang="pl">{escape(line)}</seg>')

    # Zamknij ostatniego <sp> jeśli trzeba
    if inside_sp:
        output.append('  </sp>')

    output.extend(['</body>', '</text>', '</TEI>'])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))



# remove_empty_lines('conv2.txt')
# extract_signatures('conv2.txt', 'sign2.json')
# extract_custos('conv2.txt', 'custos2.json')
# remove_parens('conv2.txt')
# merge_lines_1('conv2.txt')
# merge_lines_2('conv2.txt')
# convert_to_tei("conv2.txt", "conv2.xml")
# signatures_from_json('conv2.xml', 'sign2.json')
custos_from_json('conv2.xml', 'custos2.json')
