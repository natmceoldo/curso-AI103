import requests

url = "https://api.github.com/users/octocat"

resp = requests.get(url, timeout=10)

print(resp.status_code)

if resp.status_code == 200:
    print("Deu certo!")
elif resp.status_code == 404:
    print("Não encontrado.")
elif resp.status_code == 401:
    print("Sem autorização (401): falta chave de API.")
elif resp.status_code == 429:
    print("Muitas requisições (429): espere um pouco.")
else:
    print(f"Outro status: ({resp.status_code})")



print(f"Usuário: {dados['login']}")
print(f"Atualizado em: {dados['updated_at']}")
print(f"Repositórios públicos: {dados['public_repos']}")

try:
    resp = requests.get(url, timeout=10)

except requests.exceptions.RequestException as erro:
    raise SystemExit(f"Falha de rede: {erro}")

dados = resp.json()