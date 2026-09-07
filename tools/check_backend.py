"""Check the frontend's actual module attributes and call shapes, without IO."""
import ast
import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def validate(root=ROOT):
    boundary = ast.parse((root / "frontend/backend.py").read_text(encoding="utf8"))
    names = {alias.name for node in ast.walk(boundary)
             if isinstance(node, ast.ImportFrom) and node.module == "core"
             for alias in node.names}
    modules = {name: importlib.import_module("core." + name) for name in names}
    errors = []
    checked = set()
    for path in (root / "frontend").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                module = modules.get(node.value.id)
                if module is not None:
                    checked.add((node.value.id, node.attr))
                    if not hasattr(module, node.attr):
                        errors.append(f"{path.name}:{node.lineno}: missing {node.value.id}.{node.attr}")
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            func = node.func
            if not isinstance(func.value, ast.Name) or func.value.id not in modules:
                continue
            target = getattr(modules[func.value.id], func.attr, None)
            if target is None or not callable(target):
                continue
            if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
                continue
            try:
                signature = inspect.signature(target)
            except (ValueError, TypeError):
                continue
            try:
                signature.bind(*[None for _ in node.args], **{k.arg: None for k in node.keywords})
            except TypeError as exc:
                errors.append(f"{path.name}:{node.lineno}: {func.value.id}.{func.attr}: {exc}")
    if errors:
        raise RuntimeError("Backend API incompatibility:\n" + "\n".join(sorted(set(errors))))
    print(f"Backend contract OK: {len(checked)} attributes, frontend call signatures validated.")


if __name__ == "__main__":
    validate()
