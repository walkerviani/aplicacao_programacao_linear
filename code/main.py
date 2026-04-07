# Importar a biblioteca pulp
from pulp import *

prob = LpProblem("Problema", LpMaximize)

# Não negatividade
x = LpVariable("x", 0)
y = LpVariable("y", 0)

# FO MAX
prob += 8 * x + 10 * y, "obj"

# Restrições
prob += x + 3 * y <= 120, "r1"
prob += 3 * x + 4 * y <= 160, "r2"

prob.solve()

for variable in prob.variables():
    print(variable.name, "=", variable.varValue)

print("objective: ", value(prob.objective))

