# ============================================================
# Lab 3 - Chamada de função (function calling)
#
# Ideia central: o modelo NÃO executa as suas funções.
# Ele só PEDE para chamar uma ("function_call"). Quem executa é este
# programa; depois devolvemos o resultado e o modelo escreve a resposta final.
# ============================================================
import os
import json                      # para ler os argumentos que o modelo manda (vêm em texto JSON)
from datetime import datetime    # para pegar a hora atual
from dotenv import load_dotenv   # lê o arquivo .env
from openai import OpenAI        # cliente que conversa com o modelo
from azure.identity import DefaultAzureCredential, get_bearer_token_provider   # login sem chave (az login)


# ------------------------------------------------------------
# PASSO 1: as funções reais do seu aplicativo
# São funções Python comuns. O modelo nunca as vê: ele só vê a descrição (passo 2).
# ------------------------------------------------------------
def get_time():
    # devolve a data e a hora de agora, como texto
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_order_status(order_id: str):
    # "banco de dados" de mentira: número do pedido -> situação
    pedidos = {"1001": "enviado", "1002": "em separação", "1003": "entregue"}
    # .get devolve a situação; se o pedido não existir, devolve a frase padrão
    return pedidos.get(order_id, "pedido não encontrado")


# Tabela que liga o NOME que o modelo vai usar à função real.
# Os nomes aqui e no TOOLS (abaixo) precisam ser IGUAIS.
FUNCOES = {"get_time": get_time, "get_order_status": get_order_status}

# ------------------------------------------------------------
# PASSO 2: a descrição das funções
# É isto que o modelo lê para decidir se e qual função chamar.
# Descrição vaga = modelo escolhendo errado. Escreva claro (em inglês funciona melhor).
# ------------------------------------------------------------
TOOLS = [
    {
        "type": "function",                          # tipo de ferramenta: função nossa
        "name": "get_time",                          # nome (igual ao de FUNCOES)
        "description": "Get the current date and time",   # quando usar: o modelo decide por aqui
        # esta função não recebe nada, então não há parâmetros
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the status of an order by its id",
        "parameters": {
            "type": "object",
            # o que a função recebe: um texto chamado order_id
            "properties": {"order_id": {"type": "string", "description": "The order id, for example 1001"}},
            "required": ["order_id"],                # order_id é obrigatório
            "additionalProperties": False,           # não aceita nenhum outro parâmetro
        },
    },
]


def executar(item):
    """Executa a função que o modelo pediu e devolve o resultado em texto."""
    # procura a função pelo nome que o modelo mandou
    funcao = FUNCOES.get(item.name)
    if funcao is None:
        # o modelo pediu uma função que não existe: avisamos em vez de travar
        return f"erro: a função {item.name} não existe"
    try:
        # os argumentos chegam em texto JSON, ex.: '{"order_id": "1002"}'; viram um dicionário
        args = json.loads(item.arguments or "{}")
        # **args "abre" o dicionário: get_order_status(order_id="1002")
        resultado = funcao(**args)
        # linha de aviso para você ver que a função foi chamada
        print(f"[função chamada: {item.name} {args} -> {resultado}]")
        return str(resultado)   # o resultado volta ao modelo como texto
    except Exception as erro:   # quem trata o erro é o aplicativo, não o modelo
        print(f"[erro na função {item.name}: {erro}]")
        return f"erro: {erro}"  # o modelo lê o erro e explica ao usuário


def main():
    # lê a configuração do .env (dentro do getenv vai o NOME da variável, nunca o valor)
    load_dotenv()
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    # conexão com o modelo, sem chave: usa o seu az login
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    client = OpenAI(base_url=endpoint, api_key=token_provider)

    # histórico da conversa. Aqui guardamos tudo nós mesmos (sem previous_response_id).
    # "developer" = instrução geral para o modelo (parecido com "system")
    messages = [{"role": "developer", "content": "You are a store assistant. Use the functions to answer."}]

    while True:   # repete até o usuário digitar quit
        texto = input('\nEnter a prompt (or type "quit" to exit): ')
        if texto.lower() == "quit":
            break
        if not texto:   # linha vazia: volta a perguntar
            continue
        # guarda a pergunta do usuário no histórico
        messages.append({"role": "user", "content": texto})

        # --------------------------------------------------------
        # PASSO 3: chamar o modelo e, se ele pedir funções, executar e chamar de novo.
        # O "for" limita a 5 voltas para nunca ficar preso num laço infinito.
        # --------------------------------------------------------
        for _ in range(5):
            # envia o histórico e a lista de funções disponíveis (tools)
            response = client.responses.create(model=model, input=messages, tools=TOOLS)
            # guarda tudo o que o modelo devolveu no histórico (inclusive os pedidos de função)
            messages += response.output

            # separa só os itens do tipo "function_call" (pedidos de função)
            pedidos = [item for item in response.output if item.type == "function_call"]
            if not pedidos:
                break   # o modelo não pediu função: a resposta final já está pronta

            # ----------------------------------------------------
            # PASSO 4: executar cada função pedida e devolver o resultado ao modelo.
            # O call_id liga o resultado ao pedido certo (o modelo pode pedir várias de uma vez).
            # ----------------------------------------------------
            for item in pedidos:
                messages.append(
                    {"type": "function_call_output", "call_id": item.call_id, "output": executar(item)}
                )
            # volta ao início do "for": o modelo recebe os resultados e escreve a resposta

        # --------------------------------------------------------
        # PASSO 5: a resposta final, escrita pelo modelo com base nos resultados
        # --------------------------------------------------------
        print(response.output_text)


if __name__ == "__main__":
    main()