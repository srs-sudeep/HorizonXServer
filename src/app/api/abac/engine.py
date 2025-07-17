import re


class ABACEngine:
    OPERATORS = {
        "eq": lambda a, b: a == b,
        "neq": lambda a, b: a != b,
        "in": lambda a, b: b in a if isinstance(a, (list, set, tuple, str)) else False,
        "startswith": lambda a, b: isinstance(a, str) and a.startswith(b),
        "endswith": lambda a, b: isinstance(a, str) and a.endswith(b),
        "lt": lambda a, b: a < b,
        "gt": lambda a, b: a > b,
        "and": lambda *args: all(args),
        "or": lambda *args: any(args),
        "not": lambda a: not a,
        "len": lambda a: len(a) if a is not None else 0,
        "contains": lambda a, b: b in a
        if isinstance(a, (list, set, tuple, str))
        else False,
        "regexMatch": lambda pattern, value: bool(re.match(pattern, value))
        if isinstance(value, str)
        else False,
    }

    def __init__(self, context: dict):
        self.context = context

    def evaluate(self, expr):
        print(f"Evaluating expression: {expr}")
        if isinstance(expr, dict):
            if "var" in expr:
                return self.resolve_var(expr["var"])
            for op, args in expr.items():
                if op == "if":
                    if not isinstance(args, list) or len(args) < 2:
                        raise ValueError('"if" operator requires at least 2 arguments')
                    condition = self.evaluate(args[0])
                    if condition:
                        return self.evaluate(args[1])
                    elif len(args) > 2:
                        return self.evaluate(args[2])
                    else:
                        return None
                if op not in self.OPERATORS:
                    raise ValueError(f"Unknown operator: {op}")
                if not isinstance(args, list):
                    args = [args]
                eval_args = [self.evaluate(arg) for arg in args]
                return self.OPERATORS[op](*eval_args)
        return expr

    def resolve_var(self, var_path: str):
        parts = var_path.split(".")
        value = self.context
        for part in parts:
            if not isinstance(value, dict):
                return None
            value = value.get(part)
            if value is None:
                return None
        return value