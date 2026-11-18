import os
from dotenv import load_dotenv

load_dotenv()

chave = os.getenv("MINHA_CHAVE")

endpoint = os.getenv("ENDPOINT", "https://valor-padrao.local")

if chave is None:
    raise SystemExit ("MINHA_CHAVE não encontrada. Confira o arquivo .env")

print(f"Chave carregada: {chave[:4]}**** | endpoint: {endpoint}")