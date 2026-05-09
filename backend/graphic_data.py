from .lp_solver import get_result
import re

def get_lines() -> list:
    result = get_result()

    if not result.get("success"):
        return []

    variables = result["parts"][2]
    constraints = result["constraints"]

    if len(variables) < 2:
        return []

    # Take the optimal values to define the visual range
    obj_vars_values = list(result["variables"].values())

    # Guard against zero optimal values to avoid invisible lines in the graph
    x_max = max(obj_vars_values[0] * 3, 10) if len(obj_vars_values) > 0 else 10
    y_max = max(obj_vars_values[1] * 3, 10) if len(obj_vars_values) > 1 else 10

    lines = []

    for constraint in constraints:
        equation = re.sub(r"(<=|>=|<|>)", "=", constraint)

        if "=" not in equation:
            continue

        left_side, right_side = equation.split("=")

        try:
            right_side = float(right_side)
        except ValueError:
            continue

        try:
            coef_x = eval(left_side, {}, {variables[0]: 1, variables[1]: 0})
            coef_y = eval(left_side, {}, {variables[0]: 0, variables[1]: 1})
        except Exception:
            continue

        if coef_x == 0 and coef_y == 0:
            continue

        if coef_y != 0 and coef_x != 0:
            x_pts = [0.0, right_side / coef_x]
            y_pts = [right_side / coef_y, 0.0]

        elif coef_y == 0:
            x_val = right_side / coef_x
            x_pts = [x_val, x_val]
            y_pts = [0.0, y_max]

        else:
            y_val = right_side / coef_y
            x_pts = [0.0, x_max]
            y_pts = [y_val, y_val]

        lines.append((x_pts, y_pts))

    return lines