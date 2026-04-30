from .lp_solver import get_result
import re

def get_lines() -> list:
    result = get_result()

    if not result.get("success"):
        return []

    variables = result["parts"][2].split(";") # Ex: ["x", "y"]
    constraints = result["constraints"] # Ex: ["3*x+2*y<=90", ...]

    # Take the optimal values to define the visual range
    obj_vars_values = list(result["variables"].values())

    # Guard against zero optimal values to avoid invisible lines in the graph
    x_max = max(obj_vars_values[0] * 3, 10) if len(obj_vars_values) > 0 else 10
    y_max = max(obj_vars_values[1] * 3, 10) if len(obj_vars_values) > 1 else 10

    lines = []
    for constraint in constraints:
        equation = re.sub(r"<=|>=|<|>", "=", constraint)  # Ex: "3*x+2*y=90"

        if "=" not in equation:
            continue

        left_side, right_side = equation.split("=")

        try:
            right_side = float(right_side)
        except ValueError:
            continue

        x = eval(left_side, {}, {variables[0]: 1, variables[1]: 0})
        y = eval(left_side, {}, {variables[0]: 0, variables[1]: 1})

        if y != 0 and x != 0:
            # Diagonal line: connects Y-intercept to X-intercept
            x_pts = [0.0, right_side / x]
            y_pts = [right_side / y, 0.0]
        elif y == 0:
            # Vertical line: x = constant
            x_val = right_side / x
            x_pts = [x_val, x_val]
            y_pts = [0.0, y_max] # Uses y_max of the graph
        else:
            # Horizontal line: y = constant
            y_val = right_side / y
            x_pts = [0.0, x_max]  # Uses x_max of the graph
            y_pts = [y_val, y_val]

        lines.append((x_pts, y_pts))

    return lines