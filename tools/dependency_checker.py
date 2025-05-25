import os
import ast

def extract_imports_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    return imports

def extract_imports_from_project(path):
    all_imports = set()
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname.endswith('.py'):
                full_path = os.path.join(root, fname)
                try:
                    imports = extract_imports_from_file(full_path)
                    all_imports.update(imports)
                except Exception:
                    continue  # skip unreadable files
    return all_imports

def parse_requirements(requirements_path="requirements.txt"):
    if not os.path.exists(requirements_path):
        return None  # File not found
    declared = set()
    with open(requirements_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                declared.add(line.split('==')[0].split('>=')[0].strip())
    return declared

def run_dependency_check(project_path="."):
    requirements_path = os.path.join(project_path, "requirements.txt")
    used_imports = extract_imports_from_project(project_path)
    declared_deps = parse_requirements(requirements_path)

    if declared_deps is None:
        return {
            "status": "fail",
            "message": "requirements.txt not found. Cannot validate dependencies."
        }

    missing = used_imports - declared_deps
    unused = declared_deps - used_imports

    status = "pass" if not missing else "fail"

    msg_lines = []
    msg_lines.append(f"Imported packages detected: {len(used_imports)}")
    msg_lines.append(f"Declared packages in requirements.txt: {len(declared_deps)}")

    if missing:
        msg_lines.append(f"! Missing declarations: {', '.join(sorted(missing))}")
    if unused:
        msg_lines.append(f"! Unused declarations: {', '.join(sorted(unused))}")

    return {
        "status": status,
        "missing": list(missing),
        "unused": list(unused),
        "message": "<br>".join(msg_lines)
    }
