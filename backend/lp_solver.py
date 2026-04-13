from pulp import *
from .config_api import request_ai

# Result dictionary
_result = {
    "success": False,
    "variables": {},
    "of": None,
    "of_value": None,
    "of_type": None,
    "constraints": [],
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

    # Check if follows the pattern {   }
    response = response.strip()
    if not response.startswith("{") or not response.endswith("}"):
        _result = {"success": False, "error": response}
        return _result
    
    # Check if the problem is valid
    if response == "{}":
        _result = {
            "success": False,
            "error": "This doesn't seem to be a Linear Programming problem"
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

        # Constraints
        constraints = parts[3].split(";")  # Ex: ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
        for k, c in enumerate(constraints, 1):
            match = re.search(r'(<=|>=|=)(.*)$', c)
            if not match or match.group(2).strip() == "":
                _result = {
                    "success": False,
                    "error": f"Invalid AI-generated constraint: '{c}'. Try again"
                }
                return _result
            prob += eval(c, {}, variables), f"r{k}"

        prob.solve()

        _result = {
            "success": True,
            "variables": {v.name: v.value() for v in prob.variables()}, # Ex: {"x": 10.0, "y": 20.0}
            "of": prob.objective, # Ex: "50*x+30*y"
            "of_value": value(prob.objective), # Ex: 800.0 
            "of_type": parts[0], # Ex: "LpMaximize"
            "constraints": constraints, # Ex: ["4*x+2*y<=100", "3*x+2*y<=90", "y>=10"]
            "parts": parts
        }
        return _result
    
    except Exception as e:
        _result = {
            "success": False,
            "error": "AI's answer is wrong. Try again"
        }
        return _result