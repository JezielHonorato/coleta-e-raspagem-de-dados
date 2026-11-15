import os
import csv
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

headers = {
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/User-Agent/Firefox
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
}


def scrape_wikipedia_pib(
    save_file: str = "scrape_wikipedia_pib", extension: str = "csv"
) -> None:
    """
    Esta função coleta uma tabela com valores do PIB (Produto Interno Bruto) dos países utilizando web scraping.
    O uso desta ferramenta é permitido, conforme https://pt.wikipedia.org/wiki/robots.txt.
    """
    # Validações
    extension = extension.lower()
    if extension not in ("csv", "json"):
        print("Formato inválido, por gentileza usar 'csv' ou 'json' como parâmetro.")
        return

    url = "https://pt.wikipedia.org/wiki/Lista_de_pa%C3%ADses_por_PIB_nominal"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tabela = soup.find("table", {"class": "wikitable"})

    if tabela:
        # Definir um cabeçalho fixo para substituir o da Wikipedia
        cabecalho_fixo = [
            "pais",
            "regiao",
            "fmi_estimativa_dolar",
            "fmi_ano",
            "banco_mundial_estimativa_dolar",
            "banco_mundial_ano",
            "nacoes_unidas_estimativa_dolar",
            "nacoes_unidas_ano",
        ]

        linhas_dados = [cabecalho_fixo]

        for linha in tabela.find_all("tr"):
            # Ignorar cabeçalho original da Wikipedia
            if linha.find_all("th"):
                continue

            colunas = linha.find_all("td")
            valores = [col.get_text(strip=True) for col in colunas]

            if valores:
                linhas_dados.append(valores)

        filename = f"{save_file}.{extension}"

        # Salva em CSV
        if extension == "csv":
            with open(filename, mode="w", newline="", encoding="utf-8") as arquivo_csv:
                writer = csv.writer(arquivo_csv)
                writer.writerows(linhas_dados)

        # Salva em JSON
        elif extension == "json":
            with open(filename, mode="w", encoding="utf-8") as arquivo_json:
                json.dump(linhas_dados, arquivo_json, ensure_ascii=False, indent=4)

        print(f"O arquivo '{filename}' foi gerado com sucesso!\n")

        # Mostra as primeiras 3 linhas no console
        print(f"Primeiras 3/{len(linhas_dados)} linhas salvas em '{filename}':")
        for linha in linhas_dados[:3]:
            print(linha)

    else:
        print("Tabela não encontrada na página.")


def restcountries_api():
    base_url = "https://api.restcountries.com/countries/v5"
    response_fields = "names.translations.por.common,population,area"
    limit = 100  # Limite max da API (default = 25)
    total_paginas = 3

    todos_paises = []

    print("Consultando a API em páginas...")

    for pagina in range(total_paginas):
        offset = pagina * limit
        url = f"{base_url}?response_fields={response_fields}&limit={limit}&offset={offset}"

        try:
            print(f"Buscando página {pagina + 1} (offset={offset})...")
            response = requests.get(
                url,
                headers={
                    "Authorization": os.getenv(
                        "RESTCOUNTRIES_API", "Bearer rc_live_demo"
                    )
                },
            )
            response.raise_for_status()

            resposta_json = response.json()
            paises = resposta_json.get("data", {}).get("objects", [])

            todos_paises.extend(paises)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a API na página {pagina + 1}: {e}")
            break

    filename = "paises_populacao_area.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as arquivo_csv:
        writer = csv.writer(arquivo_csv)
        writer.writerow(["pais", "populacao", "area_km2"])

        for pais in todos_paises:
            if not isinstance(pais, dict):
                continue

            nome = (
                pais.get("names", {})
                .get("translations", {})
                .get("por", {})
                .get("common", "Desconhecido")
            )
            populacao = pais.get("population", 0)
            area = pais.get("kilometers", 0)

            writer.writerow([nome, populacao, area])

    print(f"O arquivo '{filename}' foi gerado com sucesso")


# scrape_wikipedia_pib(save_file="pib_paises", extension="csv")
# restcountries_api()
