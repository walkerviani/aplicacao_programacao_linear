from .lp_solver import get_result
import re

def get_lines():
    result = get_result()
    variables = result["parts"][2].split(";") # Ex: ["x", "y"]
    restrictions = result["restrictions"] # Ex: ["3*x+2*y<=90", ...]
    
    # Take the optimal values ​​to define the visual range
    obj_vars_values = list(result["variables"].values())
    x_max = obj_vars_values[0] * 3
    y_max = obj_vars_values[1] * 3

    lines = []

    for k, restriction in enumerate(restrictions):
        equation = re.sub(r"<=|>=|<|>", "=", restriction)  # Ex: "3*x+2*y=90"
        left_side, right_side = equation.split("=")
        right_side = float(right_side)

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