from openai import OpenAI
from google import genai

# Dictionary
_config = {}

# API key getter and setter
def get_api_key() -> str:
    return _config.get("api_key")

def set_api_key(key: str):
    _config["api_key"] = key

# Each API key provider has a specif prefix. Here are the most common and free models being set
PREFIXES = {
    "AIza": ("gemini", "GEMINI_API_KEY", "gemini-2.5-flash"),
    "sk-or-":   ("openrouter","OPENROUTER_API_KEY",  "openrouter/auto")
}

# Detect the API key and set into the dictionary
def detect_provider(key: str):
    for prefix, (provider, env_var, model) in PREFIXES.items():
        if key.startswith(prefix):
            _config["provider"] = provider
            _config["env_var"] = env_var
            _config["model"] = model
            return provider, env_var, model
    return None, None, None

# Message getter and setter
def get_message() -> dict:
    return _config.get("message")

def set_message(msg: str):
    reasoning_prompt = (
        f"Analise este problema de Programação Linear e estruture os dados:\n"
        f"1) Monte uma tabela: Variável | Preço | Custo | Margem% | Lucro | Recursos consumidos | Limites\n"
        f"2) Calcule o lucro de cada variável:\n"
        f"   - Preço + Custo: lucro = preço - custo\n"
        f"   - Preço + Custo + Margem: lucro = preço / (1.0 + margem%) - custo\n"
        f"   - Lucro + Margem (sem preço): custo = lucro / (1.0 + margem%); use lucro informado no FO\n"
        f"   - Só Lucro: use diretamente no FO\n"
        f"3) Identifique a função objetivo (maximizar ou minimizar)\n"
        f"4) Liste todas as restrições com coeficientes corretos\n\n"
        f"[PROBLEMA] {msg}"
    )

    format_prompt_template = (
        f"Com base na análise abaixo, retorne APENAS esta linha, sem explicações, sem quebras:\n"
        f"{{tipo, função_objetivo, variáveis, restrições}}\n"
        f"- tipo: 'LpMaximize' ou 'LpMinimize'\n"
        f"- função_objetivo: ex: 3.5*x+4*y\n"
        f"- variáveis: separadas por ';', ex: x;y\n"
        f"- restrições: separadas por ';', ex: 5*x+4*y<=1200;x>=0\n"
        f"[EXEMPLO] {{LpMaximize, 50*x+30*y, x;y, 4*x+2*y<=100;3*x+2*y<=90;y>=10}}\n\n"
        f"[ANÁLISE]\n{{reasoning}}"
    )

    _config["reasoning_prompt"]       = reasoning_prompt
    _config["format_prompt_template"] = format_prompt_template
    _config["message"] = {"model": _config["model"]}

# Executes the call and handles the AI ​response
def call_api(prompt: str) -> str:
    provider = _config.get("provider")
    model = _config.get("model")

    if provider == "gemini":
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()

    elif provider == "openrouter":
        client = OpenAI(api_key=get_api_key(), base_url="https://openrouter.ai/api/v1")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    return "Provider não configurado."

# Execute two-shot: reasoning → formatting
def request_ai():
    provider = _config.get("provider")
    if not provider:
        return "Configuração ausente."

    try:
        # Call 1: reasoning
        reasoning = call_api(_config["reasoning_prompt"])

        # Call 2: formatting
        format_prompt = _config["format_prompt_template"].replace("{reasoning}", reasoning)
        result = call_api(format_prompt)

        return result

    except Exception as e:
        return f"Erro na requisição: {e}"