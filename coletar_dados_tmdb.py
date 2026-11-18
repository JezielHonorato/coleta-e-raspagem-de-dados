import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")

# Verifica se a variavel de ambiente existe e nao e o texto de exemplo
if not TMDB_KEY or TMDB_KEY.strip() == "seu_token_ou_api_key_aqui":
    print("\n[ERRO] Chave da API do TMDB nao configurada!")
    print("Abra o arquivo .env e substitua 'seu_token_ou_api_key_aqui' pela sua chave real.\n")
    exit(1)

BASE_URL = "https://api.themoviedb.org/3"

# Suporte tanto para Token Bearer v4 quanto API Key v3
HEADERS = {"accept": "application/json"}
PARAMETROS_PADRAO = {}

if len(TMDB_KEY) > 50:
    HEADERS["Authorization"] = f"Bearer {TMDB_KEY}"
else:
    PARAMETROS_PADRAO["api_key"] = TMDB_KEY


def validar_token() -> bool:
    """
    Testa se a chave/token é válida.
    """
    url = f"{BASE_URL}/authentication"
    try:
        response = requests.get(url, headers=HEADERS, params=PARAMETROS_PADRAO, timeout=10)
        
        if response.status_code == 200:
            print("Autenticação no TMDB realizada com sucesso!")
            return True
        elif response.status_code == 401:
            print("\nErro!Token ou API Key invalida!")
            print("O TMDB rejeitou a credencial informada no arquivo .env.")
            print("Verifique se copiou a chave corretamente em https://www.themoviedb.org/settings/api\n")
            return False
        else:
            print(f"\n[AVISO] Resposta inesperada do TMDB (Status {response.status_code}): {response.text}\n")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERRO DE CONEXAO] Nao foi possivel conectar ao TMDB: {e}\n")
        return False

if __name__ == "__main__":
    validar_token()