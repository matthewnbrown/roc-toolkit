from sympy import sympify, solve  # py -m pip install sympy


class EquationSolver():
    ops = ['*', '/', '-', '+']

    def __rsolve(eq1: str,  eq2: str, op) -> int:
        eq1 = eq1.strip()
        if eq1 == '':
            v1 = 0
        else:
            req1 = EquationSolver.solve_equation(eq1)
            v1 = int(req1)
        v2 = int(EquationSolver.solve_equation(eq2))
        print(f'Got {v1} {op} {v2}')
        if op == '*':
            return v1 * v2
        if op == '/':
            return v1 / v2
        if op == '-':
            return v1 - v2
        if op == '+':
            return v1 + v2

    def solve_equation(eq: str) -> str:
        sym_eq = sympify(f'Eq(x,{eq})')
        res = solve(sym_eq)
        return str(res[0])

        # eq = eq.strip()
        # for op in EquationSolver.ops:
        #     if op in eq:
        #         l, r = eq.split(op, 1)
        #         return str(EquationSolver.__rsolve(l,r,op))
        # return eq
