import pulp
from pulp import COIN_CMD
from .config_api import request_ai
import re
import json

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

def solve_linear_problem() -> dict:
    global _result

    response = request_ai()
    response = response.strip()

    # Handle timeout or API errors (string responses)
    if response.startswith("Request timed out") or response.startswith("Invalid") or response.startswith("An unexpected"):
        return {
            "success": False,
            "error": response
        }

    # Check if AI flagged as invalid LP problem
    if response.strip('"') == "INVALID":
        return {
            "success": False,
            "error": "This doesn't seem to be a Linear Programming problem"
        }

    try:
        # Parse JSON safely
        try:
            clean = extract_json(response)

            if not clean:
                return {
                    "success": False,
                    "error": f"Invalid AI response (no JSON found): {response}"
                }

            parsed = json.loads(clean)
        except Exception:
            return {
                "success": False,
                "error": "Invalid AI response format (expected JSON)"
            }

        # Validate required keys
        required_keys = ["type", "objective", "variables", "constraints"]
        if not all(k in parsed for k in required_keys):
            return {
                "success": False,
                "error": "Incomplete AI response"
            }

        # Extract fields
        function_objective = str(parsed.get("type")).strip()
        obj_expr = str(parsed.get("objective")).strip()

        variables_str = parsed.get("variables", [])
        constraints = parsed.get("constraints", [])

        # Validate objective type
        if not isinstance(variables_str, list) or not isinstance(constraints, list):
            return {
                "success": False,
                "error": "Invalid AI response structure"
            }

        function_objective_type = (
            pulp.LpMaximize if function_objective == "LpMaximize"
            else pulp.LpMinimize
        )

        prob = pulp.LpProblem("Problem", function_objective_type)

        # Validate variable names
        invalid_var_names = [
            v for v in variables_str if not re.match(r'^\w+$', v)
        ]
        if invalid_var_names:
            return {
                "success": False,
                "error": f"Invalid variable names: {invalid_var_names}"
            }

        # Create variables
        variables = {
            v: pulp.LpVariable(v, lowBound=0)
            for v in variables_str
        }

        # Validate objective expression
        safe_pattern = re.compile(r'^[\d\w\s\*\+\-\.]+$')
        if not obj_expr or not safe_pattern.match(obj_expr):
            return {
                "success": False,
                "error": f"Invalid objective function: '{obj_expr}'"
            }

        # Set objective
        try:
            prob += eval(obj_expr, {"__builtins__": {}}, variables), "obj"
        except Exception:
            return {
                "success": False,
                "error": f"Failed to parse objective function: '{obj_expr}'"
            }

        # Remove non-negativity constraints
        constraints = [
            c for c in constraints
            if not re.match(r'^\w+\s*>=\s*0$', c)
        ]

        # Validate constraints
        safe_constraint_pattern = re.compile(r'^[\d\w\s\*\+\-\.\<\>=]+$')

        for k, c in enumerate(constraints, 1):

            if not safe_constraint_pattern.match(c):
                return {
                    "success": False,
                    "error": f"Invalid constraint: '{c}'"
                }

            match = re.search(r'(<=|>=|=)(.*)$', c)
            if not match or not match.group(2).strip():
                return {
                    "success": False,
                    "error": f"Invalid constraint: '{c}'"
                }

            try:
                prob += eval(c, {"__builtins__": {}}, variables), f"r{k}"
            except Exception:
                return {
                    "success": False,
                    "error": f"Failed to parse constraint: '{c}'"
                }

        prob.solve(COIN_CMD(path=get_cbc_path(), msg=0))

        # Validate objective exists
        if prob.objective is None:
            return {
                "success": False,
                "error": "Objective function not defined"
            }

        _result = {
            "success": True,
            "variables": {v.name: v.value() for v in prob.variables()},
            "of": prob.objective,
            "of_value": pulp.value(prob.objective),
            "of_type": function_objective,
            "constraints": constraints,
            "parts": [function_objective, obj_expr, variables_str, constraints]
        }

        return _result

    except Exception as e:
        return {
            "success": False,
            "error": f"AI's answer is wrong: {e}"
        }
    
def extract_json(text: str) -> str:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else ""

def insert_multiplication(expr: str) -> str:
    # # Insert * between number and variable: 1.5x → 1.5*x
    return re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

import os
import sys

def get_cbc_path():
    base_dir = os.path.dirname(sys.executable)
    
    path = os.path.join(base_dir, "cbc", "cbc.exe")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"cbc.exe not found in: {path}\n"
            f"Make sure the /cbc folder is included with the executable."
        )

    return path