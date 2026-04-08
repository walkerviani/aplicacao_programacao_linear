from config import set_api_key, get_api_key, _config, get_response, set_response, detect_provider
from openai import OpenAI
import anthropic
from google import genai

set_api_key(input("Digite sua chave API: "))
detect_provider(get_api_key())
print(f"Provedor detectado: {_config["provider"]}")

message = input("Escreva o problema de programação linear: ")
set_response(
    f"Você vai resolver o seguinte problema (após o [PROBLEMA]) de programação linear, identificando e definindo o problema, "
    f"definir variáveis de decisão (2), formular a função objetivo sendo FOMAX ou FOMIN (1) e elaborar as restrições (3). "
    f"não escreva nada além do que foi requerido a seguir, apenas siga o exemplo: "
    f"[EXEMPLO DE RESPOSTA]-> (1)FOMAX=2x_1-3x_2 (2)x_1 x_2 (3)2x_1+1x_2<=100 30x_1<=4000 x_2>=100 "
    f"[PROBLEMA]{message}"
)

def request_ai():
    provider = _config.get("provider")

    try:
        '''
        if provider == "openai":
            client = OpenAI(api_key=get_api_key())
            payload = get_response()
            response = client.chat.completions.create(
                model=payload["model"],
                messages=payload["messages"]
            )
            return response.choices[0].message.content
        '''
        
        if provider == "gemini":
            client = genai.Client(api_key=get_api_key())
            payload = get_response()
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
            payload = get_response()
            response = client.chat.completions.create(
                model=payload["model"],
                messages=payload["messages"]
            )
            return response.choices[0].message.content
    except:
        print("Algo deu errado...")

resposta = request_ai()
print(resposta)