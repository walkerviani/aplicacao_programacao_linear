from pulp import *
from .config_api import request_ai

def solve_linear_problem():
    # How the response should be like: 
    # {LpMaximize, 50*x+30*y, x;y, 4*x+2*y<=100;3*x+2*y<=90;y>=10}

    response = request_ai()
    if not response.startswith("{") or not response.endswith("}"):
            return {
                "success": False,
                "error": response
            }
    
    try:
        no_keys = response.strip("{}").strip() # Remove {}
        parts = [p.strip() for p in no_keys.split(",", 3)]  # Split into 4 parts using , 

        function_objective = parts[0] # "LpMaximize"
        function_objective_type = LpMaximize if function_objective == "LpMaximize" else LpMinimize

        prob = LpProblem("Problem", function_objective_type)

        # Variables
        variables_str = parts[2].split(";")  # ["x", "y"]
        variables = {}
        for v in variables_str:
            variables[v] = LpVariable(v, 0)

        # Objective Function
        prob += eval(parts[1], {}, variables), "obj"  # "50x+30y"

        # Restrictions
        rest_str = parts[3].split(";")  # ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
        for k, r in enumerate(rest_str, 1):
            prob += eval(r, {}, variables), f"r{k}"

        prob.solve()

        return {
            "success": True,
            "variables": {v.name: v.value() for v in prob.variables()},
            "objective": value(prob.objective)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }