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

# Response getter and setter
def get_message() -> dict:
    return _config.get("message")

def set_message(msg: str):
    content = (
    f"Você vai resolver o seguinte problema de programação linear (após [PROBLEMA]). "
    f"Retorne APENAS uma linha neste formato exato, sem explicações, sem quebras de linha: "
    f"{{tipo, função_objetivo, variáveis, restrições}} "
    f"Onde: "
    f"- tipo: exatamente 'LpMaximize' ou 'LpMinimize' "
    f"- função_objetivo: ex: 50*x+30*y (variaveis devem ser de a-z)"
    f"- variáveis: separadas por ponto e vírgula, ex: x;y "
    f"- restrições: separadas por ponto e vírgula, ex: 4*x+2*y<=100;3*x+2*y<=90;y>=10 "
    f"[EXEMPLO DE RESPOSTA] {{LpMaximize, 50*x+30*y, x;y, 4*x+2*y<=100;3*x+2*y<=90;y>=10}} "
    f"[PROBLEMA] {msg}"
)

    message_payload = {
        "model": _config["model"],
        "messages": [
            {"role": "user", "content": content}
        ]
    }
    _config["message"] = message_payload

# Executes the call and handles the AI ​response
def request_ai():
    provider = _config.get("provider")

    payload = get_message()
    if not provider or not payload:
        return "Configuração ou mensagem ausente."

    try:
        if provider == "gemini":
            client = genai.Client(api_key=get_api_key())
            response = client.models.generate_content(
                model=payload["model"],
                contents=payload["messages"][0]["content"]
            )
            return response.text
            
        elif provider == "openrouter":
            client = OpenAI(
                api_key=get_api_key(),
                base_url="https://openrouter.ai/api/v1"
            )
            response = client.chat.completions.create(
                model=payload["model"],
                messages=payload["messages"]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Erro na requisição: {e}"