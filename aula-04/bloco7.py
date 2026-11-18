import requests
import os
from dotenv import load_dotenv

url = "https://jsonplaceholder.typicode.com/posts"

params = {"userId": 1}

resp = requests.get(url, params=params ,timeout=10)
print(resp.status_code)

posts = resp.json()

print(f"recebi {len(posts)} posts")
print("títulos:")

for i in range(len(posts)):
    print(f"ID {posts[i]['id']}: {posts[i]['title']}")

load_dotenv()

chave = os.getenv("MINHA_CHAVE", "chave-de-teste")

cabecalhos = {
    "Authorization": f"Bearer {chave}",
    "Content-Type": "application/json",
}

corpo = {
    "title": "Meu primeiro POST",
    "body": "Olá, API!",
    "userId": 1
    }

resp = requests.post(url, json=corpo, headers=cabecalhos, timeout=10)

print(resp.status_code)
print(resp.json())