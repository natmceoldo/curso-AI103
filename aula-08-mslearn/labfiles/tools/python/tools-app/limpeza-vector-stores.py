import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = OpenAI(base_url=os.getenv("AZURE_OPENAI_ENDPOINT"), api_key=token_provider)

# 1. Lista os vector stores do projeto
stores = [vs for vs in client.vector_stores.list() if vs.name == "travel-brochures"]
print(f"Vector stores 'travel-brochures' encontrados: {len(stores)}")
for vs in stores:
    print(" -", vs.id)

if stores and input("Apagar todos? (s/n): ").lower() == "s":
    for vs in stores:
        client.vector_stores.delete(vs.id)
        print("apagado:", vs.id)

# 2. Lista os arquivos enviados (os PDFs ficam guardados mesmo sem o vector store)
pdfs = [f for f in client.files.list() if f.filename.lower().endswith(".pdf")]
print(f"Arquivos PDF enviados: {len(pdfs)}")
for f in pdfs:
    print(" -", f.id, f.filename)

if pdfs and input("Apagar estes PDFs? (s/n): ").lower() == "s":
    for f in pdfs:
        client.files.delete(f.id)
        print("apagado:", f.filename)
