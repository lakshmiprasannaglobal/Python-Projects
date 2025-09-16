
"""
Simple Calculator GUI using Tkinter with a safe AST evaluator.
Save as calculator.py and run: python calculator.py
"""

import tkinter as tk
from tkinter import ttk
import ast
import operator
import math

# --- Safe evaluator using AST ---
# Only allow numeric literals and these operators/functions
_allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_allowed_funcs = {
    'sqrt': math.sqrt,
    'abs': abs,
    'round': round,
}

def safe_eval(expr: str):
    """
    Evaluate a math expression safely using AST.
    Allowed: numbers, + - * / % **, parentheses, unary +/-, and some functions.
    """
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported constant")
        if isinstance(node, ast.Num):  # older AST node
            return node.n
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _allowed_operators:
                raise ValueError("Operator not allowed")
            left = _eval(node.left)
            right = _eval(node.right)
            return _allowed_operators[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _allowed_operators:
                raise ValueError("Unary operator not allowed")
            operand = _eval(node.operand)
            return _allowed_operators[op_type](operand)
        if isinstance(node, ast.Call):
            # allow simple function calls like sqrt(9)
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls allowed")
            fname = node.func.id
            if fname not in _allowed_funcs:
                raise ValueError("Function not allowed")
            args = [_eval(a) for a in node.args]
            return _allowed_funcs[fname](*args)
        if isinstance(node, ast.Expr):
            return _eval(node.value)
        if isinstance(node, ast.Tuple):
            raise ValueError("Tuples not allowed")
        raise ValueError("Unsupported expression")
    parsed = ast.parse(expr, mode='eval')
    return _eval(parsed)

# --- GUI ---
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Calculator")
        self.resizable(False, False)
        self.geometry("320x420")
        self.configure(padx=8, pady=8)

        self.expr = tk.StringVar()
        self._build_ui()
        self.bind_keys()

    def _build_ui(self):
        style = ttk.Style(self)
        style.configure("TButton", font=("Segoe UI", 12), padding=6)

        entry = ttk.Entry(self, textvariable=self.expr, font=("Segoe UI", 20), justify='right')
        entry.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0,8))
        entry.focus()

        btns = [
            ('C', 1, 0), ('⌫', 1, 1), ('%', 1, 2), ('/', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('+/-', 5, 0), ('0', 5, 1), ('.', 5, 2), ('=', 5, 3),
        ]

        for (text, r, c) in btns:
            action = lambda t=text: self.on_button(t)
            b = ttk.Button(self, text=text, command=action)
            b.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

        # Grid weight for expansion (keeps layout consistent)
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

        # small helpful label for functions
        func_label = ttk.Label(self, text="Functions: sqrt(x), abs(x), round(x,n)", font=("Segoe UI", 8))
        func_label.grid(row=6, column=0, columnspan=4, pady=(6,0))

    def bind_keys(self):
        # digits and operators
        for key in "0123456789+-*/().%":
            self.bind(key, self._key_pressed)
        self.bind('<Return>', lambda e: self.on_button('='))
        self.bind('<BackSpace>', lambda e: self.on_button('⌫'))
        self.bind('<Escape>', lambda e: self.on_button('C'))

    def _key_pressed(self, event):
        self.expr.set(self.expr.get() + event.char)

    def on_button(self, label):
        cur = self.expr.get()
        if label == 'C':
            self.expr.set('')
            return
        if label == '⌫':
            self.expr.set(cur[:-1])
            return
        if label == '=':
            self.calculate()
            return
        if label == '+/-':
            # try toggling sign for the last number
            self.toggle_sign()
            return
        # else append label
        self.expr.set(cur + label)

    def toggle_sign(self):
        s = self.expr.get().rstrip()
        if not s:
            return
        # naive approach: find last number token and flip its sign
        i = len(s)-1
        while i >= 0 and (s[i].isdigit() or s[i] == '.' ):
            i -= 1
        # now s[i] is operator or -1
        last = s[i+1:]
        prefix = s[:i+1]
        if last.startswith('-'):
            last = last[1:]
        else:
            last = f"-({last})"
        self.expr.set(prefix + last)

    def calculate(self):
        expression = self.expr.get().strip()
        if not expression:
            return
        try:
            result = safe_eval(expression)
            # format result: show int without .0
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expr.set(str(result))
        except Exception as e:
            self.expr.set("Error")

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
