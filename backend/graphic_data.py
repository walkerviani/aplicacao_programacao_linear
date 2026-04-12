from .lp_solver import get_result
import re

def get_lines():
    result = get_result()
    variables = result["parts"][2].split(";") # Ex: ["x", "y"]
    restrictions = result["restrictions"] # Ex: ["3*x+2*y<=90", ...]
    
    lines = []
    for k, restriction in enumerate(restrictions):
        equation = re.sub(r"<=|>=|<|>", "=", restriction)  # Ex: "3*x+2*y=90"
        left_side, right_side = equation.split("=")
        right_side = float(right_side)

        x = eval(left_side, {}, {variables[0]: 1, variables[1]: 0})
        y = eval(left_side, {}, {variables[0]: 0, variables[1]: 1})

        if y != 0 and x != 0:
            x_pts = [0.0, right_side / x]
            y_pts = [right_side / y, 0.0]
        elif y == 0:
            x_val = right_side / x
            x_pts = [x_val, x_val]
            y_pts = [0.0, right_side]
        else:
            y_val = right_side / y
            x_pts = [0.0, right_side]
            y_pts = [y_val, y_val]

        lines.append((x_pts, y_pts))
    return lines