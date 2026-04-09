from pulp import *
from config_api import _config, detect_provider, request_ai, set_message, set_api_key

while(1):
    api_key = input("Digite sua chave API (provedores disponíveis: OpenRouter, Gemini): ")
    if detect_provider(api_key) == (None, None, None):
        print("Chave API inválida. Tente novamente.")
    else:
        set_api_key(api_key)
        break

set_message(input("Escreva o problema de Programação Linear: "))
response = request_ai() 
# How the response should be like: 
# {LpMaximize, 50*x+30*y, x;y, 4*x+2*y<=100;3*x+2*y<=90;y>=10}
print(f"Response: {response}")

if not response.startswith("{") or not response.endswith("}"):
    print("Erro, resposta inválida.")
    print(f"Resposta: {response}")
    exit(1)

no_keys = response.strip("{}").strip() # Remove {}
parts = [p.strip() for p in no_keys.split(",", 3)]  # Split into 4 parts using ,

of = parts[0] # "LpMaximize"
of_type = LpMaximize if of == "LpMaximize" else LpMinimize
prob = LpProblem("Problem", of_type)

vars_str = parts[2].split(";")  # ["x", "y"]
variables = {}
for v in vars_str:
    variables[v] = LpVariable(v, 0)

of_str = parts[1] # "50x+30y"
prob += eval(of_str, variables), "obj"

rest_str = parts[3].split(";")  # ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
for k, r in enumerate(rest_str, 1):
    prob += eval(r, variables), f"r{k}"

prob.solve()

for variable in prob.variables():
    print(variable.name, "=", variable.varValue)

print("objective: ", value(prob.objective))