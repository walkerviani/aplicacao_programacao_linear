from pulp import *
from config_api import check_api_key, request_ai, set_message, set_api_key

while(1):
    api_key = input("Digite sua chave API (provedores disponíveis: OpenRouter, Gemini): ")
    if not check_api_key(api_key):
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

function_objective = parts[0] # "LpMaximize"
function_objective_type = LpMaximize if function_objective == "LpMaximize" else LpMinimize
prob = LpProblem("Problem", function_objective_type)

variables_str = parts[2].split(";")  # ["x", "y"]
variables = {}
for v in variables_str:
    variables[v] = LpVariable(v, 0)

function_objective_str = parts[1] # "50x+30y"
prob += eval(function_objective_str, variables), "obj"

rest_str = parts[3].split(";")  # ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
for k, r in enumerate(rest_str, 1):
    prob += eval(r, variables), f"r{k}"

prob.solve()

for v in prob.variables():
    print(v.name, "=", v.variable_value)

print("objective: ", value(prob.objective))