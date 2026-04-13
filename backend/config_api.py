from openai import OpenAI, AuthenticationError as OpenAIAuthenticationError
from google import genai
from google.genai.errors import ClientError as GenAiClientError, ServerError as GenAiServerError
from typing import Optional

# Dictionary
_config = {
    "api_key": "",
    "model": None,
    "provider": None,
    "env_var": None,
    "format_prompt_template": "",
    "reasoning_prompt": "",
    "message": {}
}

# API key getter and setter
def get_api_key() -> Optional[str]:
    return _config.get("api_key")  # type: ignore[return-value]


def set_api_key(key: str):
    _config["api_key"] = key

    try:
        check_api_key(key)
    except Exception:
        return "Invalid API key or unsupported provider. Use Gemini 2.5 Flash or Openrouter Auto. Other models are not supported"


# Each API key provider has a specific prefix.
PREFIXES = {
    "AIza": ("gemini",      "GEMINI_API_KEY",      "gemini-2.5-flash"),
    "sk-or-": ("openrouter",  "OPENROUTER_API_KEY",  "openrouter/auto"),
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
        f"ATENÇÂO: Não retorne não negatividade (Exemplo: x>=0, y>=0)"
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
    _config["reasoning_prompt"] = reasoning_prompt
    _config["format_prompt_template"] = format_prompt_template
    _config["message"] = {"model": _config["model"]}

# Executes the call and handles the AI response
def call_api(prompt: str) -> str:
    provider = _config.get("provider")
    model = _config.get("model")

    if not isinstance(model, str):
        return "Model not configured. Use Gemini 2.5 Flash or Openrouter Auto. Other models are not supported"

    if provider == "gemini":
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()

    elif provider == "openrouter":
        client = OpenAI(api_key=get_api_key(), base_url="https://openrouter.ai/api/v1")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        if content is None:
            return "Empty AI response. Try again"
        return content.strip()

    return "Provider not configured. Check your API key"

# Execute two-shot: reasoning → formatting
def request_ai() -> str:
    provider = _config.get("provider")
    if not provider:
        return "Missing configuration. Check your API key"
    try:
        # Call 1: reasoning
        reasoning = call_api(_config["reasoning_prompt"]) # type: ignore[arg-type]

        # Call 2: formatting
        format_prompt = _config["format_prompt_template"].replace( # type: ignore[union-attr]
            "{reasoning}", reasoning
        )
        return call_api(format_prompt)
    except OpenAIAuthenticationError as e:
        if e.status_code == 401:
            return f"Invalid authentication or incorrect API key provided. Check your API key"
        elif e.status_code == 403:
            return "You are accessing the API from an unsupported country, region, or territory. Change your provider"  
        elif e.status_code == 429:
            return "You've exceeded the rate limit or sending requests too quickly"
        elif e.status_code >= 503:
            return "The service may be temporarily overloaded or down. Change your provider or try again later"
        elif e.status_code >= 500:
            return "The server had an error while processing your request. Change your provider or try again later"
    except GenAiClientError as e:
        if e.code == 400:
            return "Invalid argument. Check your API key"
        elif e.code == 403:
            return "Your API key doesn't have the required permissions. Check your API key"
        elif e.code == 404:
            return "The requested resource wasn't found. Try again"
        elif e.code == 429:
            return "You've exceeded the rate limit. Change your provider, your API key or try again later"
    except GenAiServerError as e:
        if e.code >= 504:
            return "Your prompt (or context) is too large to be processed in time"
        elif e.code >= 503:
            return "The service may be temporarily overloaded or down. Change your provider or try again later"
        elif e.code >= 500:
            return "An unexpected error occurred on Google's side. Change your provider or try again later"
        
        
    return "An unexpected error occurred. Try again"