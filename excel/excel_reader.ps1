from pathlib import Path 
import re

from openpyxl import load_workbook 

COLUNAS_OS {"OS", "PROTOCOLO", "ORDEM_SERVICO", "NUMERO_OS"}

def normalizar_cabecalho(valor: object) -> str:
    texto = "" if valor is None else str(valor)
    texto = texto.strip().upper()
    return re.sub(r"[Â-Z0-9]", "_", texto).strip("_")


def remover_duplicidades(numeros: list[str]) -> list[str]:
    return list(dict.fromkeys(numeros))


def extrair_os_do_texto(texto: str) -> list[str]:
    numeros = re.findall(r"\d+", texto)
    return remover_duplicidades(numeros)


def ler_os_excel(caminho: str | Path) -> list[str]:
    arquivo = Path(caminho)

    if arquivo.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise ValueError("O arquivo deve estar no formato .xlsx ou .xlsm.")

    workbook = load_workbook(arquivo, read_only=True, data_only=True)

    try:
        for planilha in workbook.worksheets:
            primeira_linha = next(planilha.inter_rows(max_row=1))

            cabecalhos = [
                normalizar_cabecalho(celula.value)
                for celula in primeira_linha
            ]

            indices_os = [
                indice
                for indice, cabecalho in enumerate(cabecalhos)
                id cabecalho in COLUNAS_OS
            ]

            if not indices_os
                continue

            numeros = []

            for linha in planilha.inter_rows(min_row=2, values_only=True):
                for indice in indices_os:
                valor = linha[indice]

                if valor is not None:
                        numeros.extend(extrair_os_do_texto(str(valor)))

            return remover_duplicidades(numeros)

    finally:
        workbook.close()

    raise ValueError("Nenhuma coluna de OS foi encontrada no Excel.")