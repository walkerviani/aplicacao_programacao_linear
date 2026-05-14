from openai import OpenAI, AuthenticationError as OpenAIAuthenticationError
from typing import Optional
import httpx

# Dictionary
_config = {
    "api_key": "",
    "model": None,
    "provider": None,
    "env_var": None,
    "format_prompt": "",
    "reasoning_prompt": "",
    "message": {}
}

# API key getter and setter
def get_api_key() -> Optional[str]:
    return _config.get("api_key")  # type: ignore[return-value]


def set_api_key(key: str) -> Optional[str]:
    _config["api_key"] = key

    if not check_api_key(key):
        return "Invalid API key or unsupported provider."

    return None


# Each API key provider has a specific prefix.
PREFIXES = {
    "sk-or-": ("openrouter", "OPENROUTER_API_KEY", "openrouter/free"),
    "sk-": ("deepseek", "DEEPSEEK_API_KEY", "deepseek-v4-flash"),
}

# Detect the API key and set into the dictionary
def check_api_key(key: str) -> bool:
    for prefix, (provider, env_var, model) in PREFIXES.items():
        if key.startswith(prefix):
            _config["provider"] = provider
            _config["env_var"] = env_var
            _config["model"] = model
            return True
    return False


# Message getter and setter
def get_message() -> Optional[dict]:
    return _config.get("message")  # type: ignore[return-value]

def set_message(msg: str) -> None:
    reasoning_prompt = (
        f"Analise este problema de Programação Linear e estruture os dados.\n\n"
        f"ATENÇÃO: Se o problema já estiver parcialmente ou totalmente resolvido, "
        f"com função objetivo e restrições explícitas, use os valores fornecidos diretamente "
        f"sem recalcular. Apenas valide e estruture.\n\n"
        f"PASSO 1 - Monte uma tabela:\n"
        f"Variável | Preço | Custo | Margem% | Lucro | Recursos consumidos | Limites\n\n"
        f"PASSO 2 - Identifique o tipo de dado fornecido (uma das opções abaixo) e calcule o lucro:\n"
        f"   CASO A - Preço + Custo: lucro = preço - custo\n"
        f"   CASO B - Preço + Custo + Margem: lucro = preço / (1 + margem%) - custo\n"
        f"   CASO C - Lucro + Margem (sem preço): custo = lucro / (1 + margem%)\n"
        f"   CASO D - Só Lucro: usar diretamente\n"
        f"   CASO E - Preço + múltiplos custos: lucro = preço - soma(quantidade_i * custo_i)\n"
        f"   → Indique qual CASO se aplica antes de calcular.\n\n"
        f"PASSO 3 - Identifique a função objetivo:\n"
        f"   → Escreva se é maximizar ou minimizar e monte a expressão com os lucros calculados.\n\n"
        f"ATENÇÃO CRÍTICA: Os coeficientes das restrições devem ser os consumos de recursos "
        f"(kg, minutos, unidades), NUNCA preços ou lucros.\n"
        f"Exemplo correto: se cada mesa consome 8kg de madeira → coeficiente na restrição de madeira é 8.\n\n"
        f"PASSO 4 - Liste TODOS os recursos mencionados no enunciado como restrições:\n"
        f"   → Para cada recurso citado (tempo, matéria-prima, estoque, capacidade), "
        f"crie uma restrição separada.\n"
        f"   → Se um recurso aparece no enunciado mas não vira restrição, justifique.\n\n"
        f"PASSO 5 - Conferência cruzada:\n"
        f"   → Releia o enunciado e marque cada dado numérico usado.\n"
        f"   → Algum dado numérico ficou sem uso? Se sim, ele deve virar restrição ou coeficiente.\n\n"
        f"PASSO 6 - Validação (responda cada item):\n"
        f"   a) O número de coeficientes em cada restrição bate com o número de variáveis?\n"
        f"   b) A função objetivo contém todas as variáveis listadas?\n"
        f"   c) Os sinais das restrições estão corretos (<=, >= ou =)?\n"
        f"   d) Os valores calculados fazem sentido com o enunciado?\n"
        f"   e) Todos os dados numéricos do enunciado foram usados?\n\n"
        f"ATENÇÃO: Não inclua restrições de não negatividade (ex: x>=0, y>=0)\n\n"
        f"[PROBLEMA]\n{msg}"
    )

    format_prompt = (
        "Com base na análise abaixo, retorne APENAS um JSON válido. "
        "Sem explicações, sem texto antes ou depois.\n\n"
        "Formato esperado:\n"
        "{\n"
        '  "type": "LpMaximize",\n'
        '  "objective": "50*x+30*y",\n'
        '  "variables": ["x", "y"],\n'
        '  "constraints": ["4*x+2*y<=100", "3*x+2*y<=90"]\n'
        "}\n\n"
        "Regras:\n"
        "- type: deve ser exatamente 'LpMaximize' ou 'LpMinimize'\n"
        "- objective: string sem espaços\n"
        "- variables: lista de nomes de variáveis\n"
        "- constraints: lista de restrições\n"
        "- NÃO incluir restrições de não negatividade (ex: x>=0)\n"
        "- Usar ponto para decimais (3.5 e não 3,5)\n"
        "- NÃO usar markdown (sem ```)\n"
        "- NÃO incluir explicações\n\n"
        "Se não for um problema válido, retorne exatamente:\n"
        '"INVALID"\n\n'
        "ANTES de retornar, verifique:\n"
        "- O número de coeficientes em cada restrição bate com o número de variáveis?\n"
        "- A função objetivo contém todas as variáveis?\n\n"
        "[ANÁLISE]\n{reasoning}"
    )
    _config["reasoning_prompt"] = reasoning_prompt
    _config["format_prompt"] = format_prompt
    _config["message"] = {"model": _config["model"]}

# Executes the call and handles the AI response
def call_api(prompt: str) -> str:
    provider = _config.get("provider")
    model = _config.get("model")

    if not isinstance(model, str):
        return "Model not configured. Use Deepseek v4 Flash or Openrouter Free."

    if provider == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
    elif provider == "deepseek":
        base_url = "https://api.deepseek.com/v1"
    else:
        return "Provider not configured. Check your API key"

    client = OpenAI(
        api_key=get_api_key(),
        base_url=base_url,
        timeout=120.0
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    if content is None:
        return "Empty AI response. Try again"
    return content.strip()

# Execute two-shot: reasoning → formatting
def request_ai() -> str:
    if not _config.get("provider"):
        return "Missing configuration. Check your API key"
    try:
        reasoning = call_api(_config["reasoning_prompt"])
        format_prompt = _config["format_prompt"].replace("{reasoning}", reasoning)
        return call_api(format_prompt)

    except httpx.TimeoutException:
        return "Request timed out. Check your connection or try again"
    except OpenAIAuthenticationError as e:
        if e.status_code == 401:
            return "Invalid authentication or incorrect API key provided. Check your API key"
        elif e.status_code == 403:
            return "You are accessing the API from an unsupported country, region, or territory"
        elif e.status_code == 429:
            return "You've exceeded the rate limit or sending requests too quickly"
        elif e.status_code >= 503:
            return "The service may be temporarily overloaded or down. Try again later"
        elif e.status_code >= 500:
            return "The server had an error while processing your request. Try again later"
        return "An unexpected error occurred. Try again"
    except Exception as e:
        return f"An unexpected error occurred: {e}"