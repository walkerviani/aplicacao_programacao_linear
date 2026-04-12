from .lp_solver import get_result
import re
import matplotlib.pyplot as mpl

def get_lines():
    result = get_result()
    variables = result["parts"][2].split(";") # Ex: ["x", "y"]
    restrictions = result["restrictions"] # Ex: ["3*x+2*y<=90", ...]
    
    lines = []
    for restriction, k in restrictions:
        equation = re.sub(r"<=|>=|<|>", "=", restriction)  # Ex: "3*x+2*y=90"
        left_side, right_side = equation.split("=")
        right_side = float(right_side)

        # x=0, solve for y
        y = eval(left_side, {}, {variables[0]: 0, variables[1]: 1})
        y = right_side / y  # 90 / 2 = 45.0

        # set y=0, solve for x
        x = eval(left_side, {}, {variables[0]: 1, variables[1]: 0})
        x = right_side / x  # 90 / 3 = 30.0

        lines.append({
            k+1: {
                variables[0]: x,  # "x": 30.0
                variables[1]: y   # "y": 45.0
            }
        })

    return lines