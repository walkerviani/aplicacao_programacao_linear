_config = {}

# API key getter and setter
def get_api_key() -> str:
    return _config.get("api_key")

def set_api_key(key: str):
    _config["api_key"] = key

# Each API key provider has a specif prefix. Here are the most common and free models being set
PREFIXES = {
    "AIza": ("gemini", "GEMINI_API_KEY", "gemini-2.5-flash"),
    #"sk-proj-": ("openai",    "OPENAI_API_KEY",     "gpt-4o"),
    "sk-or-":   ("openrouter","OPENROUTER_API_KEY",  "openrouter/auto"),
}

def detect_provider(key: str):
    for prefix, (provider, env_var, model) in PREFIXES.items():
        if key.startswith(prefix):
            _config["provider"] = provider
            _config["env_var"] = env_var
            _config["model"] = model
            return provider, env_var, model
    return None, None, None


# Response getter and setter
def get_response() -> dict:
    return _config.get("response")

def set_response(message: str):
    response = {
        "model": _config["model"],
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    _config["response"] = response