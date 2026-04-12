from pulp import *
from .config_api import request_ai

# Result dictionary
_result = {
    "success": False,
    "variables": {},
    "of": None,
    "of_type": None,
    "restrictions": [],
    "parts": []
}

# Result getter
def get_result() -> dict:
    return _result

def solve_linear_problem():
    global _result
    # How the response should be like: 
    # {LpMaximize, 50*x+30*y, x;y, 4*x+2*y<=100;3*x+2*y<=90;y>=10}
    response = request_ai()
    if not response.startswith("{") or not response.endswith("}"):
        _result = {
            "success": False,
            "error": response
        }
        return _result

    try:
        no_keys = response.strip("{}").strip() # Remove {}
        parts = [p.strip() for p in no_keys.split(",", 3)]  # Split into 4 parts using ,

        function_objective = parts[0] # "LpMaximize or LpMinimize"
        function_objective_type = LpMaximize if function_objective == "LpMaximize" else LpMinimize

        prob = LpProblem("Problem", function_objective_type)

        # Variables
        variables_str = parts[2].split(";")  # Ex: ["x", "y"]
        variables = {}
        for v in variables_str:
            variables[v] = LpVariable(v, 0)

        # Objective Function
        prob += eval(parts[1], {}, variables), "obj"  # Ex: "50*x+30*y"

        # Restrictions
        restrictions = parts[3].split(";")  # Ex: ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
        for k, r in enumerate(restrictions, 1):
            prob += eval(r, {}, variables), f"r{k}"
        prob.solve()

        _result = {
            "success": True,
            "variables": {v.name: v.value() for v in prob.variables()},  
            "of": value(prob.objective),
            "of_type": parts[0], 
            "restrictions": restrictions,
            "parts": parts
        }
        return _result
    
    except Exception as e:
        _result = {
            "success": False,
            "error": str(e)
        }
        return _result