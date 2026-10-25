"""Ejecuta solo la lógica original, sin imports externos ni consultas HTTP."""
import ast
import contextlib
import io
from datetime import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def cargar_camisetas():
    tree = ast.parse((ROOT / 'referencia/camisetas_colab.py').read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if (
        isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'camisetas' for t in n.targets)
    ) or (isinstance(n, ast.FunctionDef) and n.name == 'seleccionar_camiseta')]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<referencia camisetas>', 'exec'), namespace)
    return namespace

def ejecutar_eventos(events):
    tree = ast.parse((ROOT / 'referencia/eventos_colab.py').read_text(encoding='utf-8'))
    start = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'TOP_ATP' for t in n.targets))
    namespace = {'events': events, 'time': time, 'EVENT_DURATION': 120,
                 'MAX_OVERLAP': 30, 'DAY_START': 7 * 60, 'DAY_END': 23 * 60 + 30}
    # Desde las preferencias hasta el final: filtros, puntuación, plan y alternativas originales.
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(ast.Module(body=tree.body[start:], type_ignores=[]), '<referencia eventos>', 'exec'), namespace)
    return namespace
