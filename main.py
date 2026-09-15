"""
Extrai os dados essenciais do Relatório Anual de Sinistralidade Rodoviária
2019 (ANSR) e gera ficheiros CSV limpos e prontos a usar.

Dados extraídos:
  1. evolucao_2010_2019.csv     -> Tabela 10: evolução global 2010-2019
  2. acidentes_por_mes.csv      -> Tabela 11: acidentes e vítimas por mês (2018 vs 2019)
  3. acidentes_por_natureza.csv -> Tabela 16: acidentes e vítimas por natureza do acidente
  4. acidentes_por_distrito.csv -> Tabela 61: acidentes e vítimas por distrito

Uso:
    uv run main.py [caminho_para_o_pdf]

Se não indicares um caminho, é usado por omissão:
    data/Relatorio-Anual-Sinistralidade-Rodoviaria-2019.pdf
"""

import csv
import re
import sys
from pathlib import Path

import pdfplumber

DEFAULT_PDF = Path("data/Relatorio-Anual-Sinistralidade-Rodoviaria-2019.pdf")
OUTPUT_DIR = Path("output")

# Números de página (1-based, como aparecem no PDF) de cada tabela-fonte.
PAGE_EVOLUCAO = 86
PAGE_MES = 87
PAGE_NATUREZA = 92
PAGE_DISTRITO = 138


def clean_number(value):
    """Remove espaços usados como separador de milhar (ex: '2 815' -> '2815')."""
    if value is None:
        return ""
    return value.replace("\xa0", " ").replace(" ", "").strip()


def extract_evolucao(pdf):
    """Tabela 10: Evolução Global 2010-2019 (uma linha por ano)."""
    page = pdf.pages[PAGE_EVOLUCAO - 1]
    table = page.extract_tables()[0]

    rows = []
    for row in table:
        if not row or not row[0] or not re.fullmatch(r"20\d{2}", row[0].strip()):
            continue
        # Colunas fixas nesta tabela: ano, AcV, %, AcVM/AcFG, %, VM, %, FG, %, FL, %, total_feridos, %, indice
        # Os valores percentuais vêm por vezes corrompidos na extração (ex.: "8-%")
        # por causa de sobreposição de texto no PDF de origem, por isso não são incluídos.
        rows.append(
            {
                "ano": row[0].strip(),
                "acidentes_com_vitimas": clean_number(row[1]),
                "acidentes_com_vitimas_mortais_ou_feridos_graves": clean_number(row[3]),
                "vitimas_mortais": clean_number(row[5]),
                "feridos_graves": clean_number(row[9]),
                "feridos_leves": clean_number(row[11]),
                "total_feridos": clean_number(row[13]),
                "indice_gravidade": row[15].strip() if row[15] else "",
            }
        )
    return rows


def extract_por_mes(pdf):
    """Tabela 11: Acidentes e vítimas por mês, 2018 vs 2019."""
    page = pdf.pages[PAGE_MES - 1]
    table = page.extract_tables()[0]

    meses_validos = {
        "jan", "fev", "mar", "abr", "mai", "jun",
        "jul", "ago", "set", "out", "nov", "dez", "Total",
    }

    rows = []
    for row in table:
        if not row or not row[0] or row[0].strip() not in meses_validos:
            continue
        mes = row[0].strip()
        for ano_idx, ano in [(0, "2018"), (1, "2019")]:
            rows.append(
                {
                    "mes": mes,
                    "ano": ano,
                    "acidentes_com_vitimas": clean_number(row[1 + ano_idx]),
                    "vitimas_mortais": clean_number(row[3 + ano_idx]),
                    "feridos_graves": clean_number(row[5 + ano_idx]),
                    "feridos_leves": clean_number(row[7 + ano_idx]),
                    "total_de_feridos": clean_number(row[9 + ano_idx]),
                    "indice_gravidade": row[11 + ano_idx].strip() if row[11 + ano_idx] else "",
                }
            )
    return rows


def _parse_natureza_entries(table):
    """
    Junta as linhas de texto embrulhado (word-wrap) desta tabela em entradas
    completas: cada entrada tem o nome da natureza do acidente, os valores
    numéricos e o texto de categoria (col. 0) recolhido em qualquer linha
    dentro do intervalo da entrada — a rótulo de categoria fica centrado
    verticalmente na célula fundida do PDF, por isso pode aparecer em
    qualquer linha do grupo, não necessariamente na primeira.
    """
    entries = []
    i, n = 0, len(table)
    while i < n:
        row = table[i]
        if not row or len(row) < 14 or row[2] is None:
            i += 1
            continue
        nome_partes = [row[1].strip()] if row[1] else []
        categoria_textos = [row[0].strip()] if row[0] and row[0].strip() else []
        valores = row[2:14]
        j = i + 1
        while j < n and table[j][2] is None:
            cont = table[j]
            if cont[0] and cont[0].strip():
                categoria_textos.append(cont[0].strip())
            if cont[1] and cont[1].strip():
                nome_partes.append(cont[1].strip())
            j += 1
        entries.append(
            {
                "nome": " ".join(nome_partes),
                "categoria_textos": categoria_textos,
                "valores": valores,
            }
        )
        i = j
    return entries


def extract_por_natureza(pdf):
    """Tabela 16: Acidentes e vítimas por natureza do acidente (categorias e subtotais)."""
    page = pdf.pages[PAGE_NATUREZA - 1]
    table = page.extract_tables()[0]
    entries = _parse_natureza_entries(table)

    rows = []
    grupo = []
    for entry in entries:
        if entry["nome"] == "Total" and entry is entries[-1]:
            categoria = ""  # total geral do relatório
            grupo_final = [entry]
        else:
            grupo.append(entry)
            if entry["nome"] != "Total":
                continue
            grupo_final = grupo
            grupo = []
            categoria_textos = [t for e in grupo_final for t in e["categoria_textos"]]
            categoria = categoria_textos[0] if categoria_textos else ""

        for e in grupo_final:
            valores = e["valores"]
            rows.append(
                {
                    "categoria": categoria,
                    "natureza_do_acidente": e["nome"],
                    "ano": "2018",
                    "acidentes_com_vitimas": clean_number(valores[0]),
                    "vitimas_mortais": clean_number(valores[2]),
                    "feridos_graves": clean_number(valores[4]),
                    "feridos_leves": clean_number(valores[6]),
                    "total_de_feridos": clean_number(valores[8]),
                    "indice_gravidade": valores[10].strip() if valores[10] else "",
                }
            )
            rows.append(
                {
                    "categoria": categoria,
                    "natureza_do_acidente": e["nome"],
                    "ano": "2019",
                    "acidentes_com_vitimas": clean_number(valores[1]),
                    "vitimas_mortais": clean_number(valores[3]),
                    "feridos_graves": clean_number(valores[5]),
                    "feridos_leves": clean_number(valores[7]),
                    "total_de_feridos": clean_number(valores[9]),
                    "indice_gravidade": valores[11].strip() if valores[11] else "",
                }
            )
    return rows


def extract_por_distrito(pdf):
    """Tabela 61: Acidentes e vítimas por distrito, 2018 vs 2019."""
    page = pdf.pages[PAGE_DISTRITO - 1]
    table = page.extract_tables()[0]

    distritos_validos = {
        "Aveiro", "Beja", "Braga", "Bragança", "Castelo Branco", "Coimbra",
        "Évora", "Faro", "Guarda", "Leiria", "Lisboa", "Portalegre", "Porto",
        "Santarém", "Setúbal", "Viana do Castelo", "Vila Real", "Viseu", "Total",
    }

    rows = []
    for row in table:
        nome = None
        for cell in row:
            if cell and cell.strip() in distritos_validos:
                nome = cell.strip()
                break
        if not nome:
            continue
        valores = [clean_number(c) for c in row if c and re.fullmatch(r"[\d\s]+", c.strip())]
        if len(valores) < 10:
            continue
        # ordem no PDF: acidentes_18, acidentes_19, vm_18, vm_19, fg_18, fg_19,
        #               fl_18, fl_19, total_18, total_19
        for ano_idx, ano in [(0, "2018"), (1, "2019")]:
            rows.append(
                {
                    "distrito": nome,
                    "ano": ano,
                    "acidentes_com_vitimas": valores[0 + ano_idx],
                    "vitimas_mortais": valores[2 + ano_idx],
                    "feridos_graves": valores[4 + ano_idx],
                    "feridos_leves": valores[6 + ano_idx],
                    "total_de_vitimas": valores[8 + ano_idx],
                }
            )
    return rows


def write_csv(rows, filename):
    if not rows:
        print(f"  [aviso] nenhuma linha extraída para {filename}, ficheiro não criado")
        return
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {path} ({len(rows)} linhas)")


def main():
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf_path.exists():
        sys.exit(f"Ficheiro PDF não encontrado: {pdf_path}")

    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"A ler {pdf_path} ...")
    with pdfplumber.open(pdf_path) as pdf:
        print("A extrair evolução global 2010-2019...")
        write_csv(extract_evolucao(pdf), "evolucao_2010_2019.csv")

        print("A extrair acidentes por mês...")
        write_csv(extract_por_mes(pdf), "acidentes_por_mes.csv")

        print("A extrair acidentes por natureza do acidente...")
        write_csv(extract_por_natureza(pdf), "acidentes_por_natureza.csv")

        print("A extrair acidentes por distrito...")
        write_csv(extract_por_distrito(pdf), "acidentes_por_distrito.csv")

    print("Concluído.")


if __name__ == "__main__":
    main()