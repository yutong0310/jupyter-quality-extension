import os
import ast
import sys
import importlib.util

# Extract imports from a single python file
def extract_imports_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            # Parse the file into an AST (Abstract Syntax Tree)
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return set()  # Skip files with syntax errors

    imports = set()
    # Walk through all nodes in the AST tree
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Handle simple "import xxx" statements
            for n in node.names:
                imports.add(n.name.split('.')[0]) # Take only the top-level module
        elif isinstance(node, ast.ImportFrom):
            # Handle "from xxx import yyy" statements
            if node.module:
                imports.add(node.module.split('.')[0]) # Only top-level module
    return imports

# Extract imports from all python files in a project
def extract_imports_from_project(path):
    all_imports = set()

    # Walk the directory tree
    for root, dirs, files in os.walk(path):

        # Skip hidden folders like .ipynb_checkpoints or virtual environments
        dirs[:] = [d for d in dirs if not d.startswith(".") and "venv" not in d and "env" not in d]

        for fname in files:
            if fname.endswith('.py'):
                full_path = os.path.join(root, fname)
                try:
                    # Extract imports from each .py file
                    imports = extract_imports_from_file(full_path)
                    all_imports.update(imports)
                except Exception:
                    continue  # Skip files that can't be read or parsed
    return all_imports

# Parse requirements.txt and extract declared packages
def parse_requirements(requirements_path="requirements.txt"):
    if not os.path.exists(requirements_path):
        return None # requirements.txt is missing
    
    declared = set()
    with open(requirements_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove version contraints (e.g., 'package==1.2.3' -> 'package')
                declared.add(line.split('==')[0].split('>=')[0].strip())
    return declared

# Check if an import is a third-party (installable) module
# Third-party Python module: a module installed via tools like pip, located in site-packages
def is_importable_third_party(module_name):
    if module_name.startswith("_"):
        return False # Skip built-in/internal modules
    try:
        spec = importlib.util.find_spec(module_name)

        if not spec or not spec.origin:
            return False
        
        # Consider only modules installed in site-packages (e.g., third-party)
        return "site-packages" in spec.origin
    except Exception:
        return False

# Run the dependency check on a project folder
def run_dependency_check(project_path="."):
    requirements_path = os.path.join(project_path, "requirements.txt")

    # Collect all imports used in the project source file 
    project_imports = extract_imports_from_project(project_path)

    # Keep only the imports taht are third-party (i.e., installed via pip)
    used_imports = {name for name in project_imports if is_importable_third_party(name)}
    # used_imports = {name.lower() for name in project_imports if is_importable_third_party(name)}
    
    # Read declared dependencies from requirements.txt
    declared_deps = parse_requirements(requirements_path)

    if declared_deps is None:
        return {
            "status": "fail",
            "message": "requirements.txt not found. Cannot validate dependencies."
        }

    # Compute missing, unused, and correctly declared dependencies 
    missing = used_imports - declared_deps
    declared_not_imported = declared_deps - used_imports
    declared_and_used = used_imports & declared_deps

    # Pass only if no missing packages
    status = "pass" if not missing else "fail"

    # Format helpers
    # def gray_block(label, content):
    #    return f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>{label}</b></div><div style='margin-left: 40px; color: gray; font-size: 90%;'>{content}</div>"

    def gray_block(label, content):
        return f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>{label}</b> {content}</div>"

    def gray_list(title, items):
        if not items:
            return ""
        return f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>{title}</b></div><div style='margin-left: 40px; color: gray; font-size: 90%;'>• {', '.join(sorted(items))}</div>"

    # Build the final message output
    msg_lines = []

    # Show summary statistics
    msg_lines.append(gray_block("Imported third-party packages found in your code:", str(len(used_imports))))
    msg_lines.append(gray_block("Packages listed in requirements.txt:", str(len(declared_deps))))
    
    # List all used and declared packages 
    msg_lines.append(gray_list("Imported packages:", used_imports))
    msg_lines.append(gray_list("Declared packages:", declared_deps))

    # Show overlap, missing, and unused dependencies
    msg_lines.append(gray_list("✓ Declared and used:", declared_and_used))
    msg_lines.append(gray_list("⚠ Declared but not imported:", declared_not_imported))
    
    if declared_not_imported:
        # Add a note about indirect imports (e.g., used via CLI)
        msg_lines.append("<div style='margin-left: 40px; color: gray; font-size: 90%;'><i>Note: Some packages may be used indirectly (e.g., by CLI tools or notebooks) and won't appear in Python imports.</i></div>")

    msg_lines.append(gray_list("✗ Missing declarations (used but not listed):", missing))

    return {
        "status": status, # pass or fail
        "missing": list(missing), # used but undeclared
        "unused": list(declared_not_imported), # declared but not used 
        "message": "".join(msg_lines) # formatted HTML report
    }
