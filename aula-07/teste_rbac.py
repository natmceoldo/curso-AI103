from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

ENDPOINT ="https://cosmesantos4-7348-resource.services.ai.azure.com/api/projects/cosmesantos4-7348"
DEPLOYMENT = "gpt-6-luna"

try:
    project = AIProjectClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())
    openai = project.get_openai_client()
    resposta = openai.responses.create(model=DEPLOYMENT, input="Crie uma cacofonia em uma frase curta.")
    print("FUNCIONOU:", resposta.output_text)
except Exception as erro:
    print("FALHOU:", type(erro).__name__)
    print(str(erro)[:400])