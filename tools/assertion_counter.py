import os
import ast

def run_assertion_percentage(path):
    """
    Calculates the percentage of 'assert' statements in a Python project.

    The tool scans all .py files under the given path (project root),
    excluding irrelevant directories, and analyzes code using Python's AST.

    Returns:
        dict: {
            "status": "pass" or "fail",
            "message": styled HTML report with counts, summary, and tip
        }
    """

    total_asserts = 0     # Total number of assert statements
    total_statements = 0  # Total number of executable Python statements
    python_files = []     # List of .py files to analyze

    # STEP 1: Define which folders should be skipped during scan 
    excluded_dirs = {
        "venv", "env", "__pycache__", ".git", ".hg", ".svn",
        ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache",
        "build", "dist", ".tox", ".nox", "site-packages",
        ".idea", ".vscode", ".DS_Store", "__pypackages__"
    }

    # STEP 2: Recursively collect .py files under project root
    if os.path.isfile(path) and path.endswith('.py'):
        python_files.append(path)

    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            # Filtering of irrelevant subdirectories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

    else:
        return {
            "status": "fail",
            "message": f"Invalid path: {path}"
        }
    
    # STEP 3: Parse each file to count assert and stmt nodes
    for filepath in python_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    total_asserts += 1
                if isinstance(node, ast.stmt):
                    total_statements += 1
        
        except Exception as e:
            # Do not block the whole analysis if one file fails 
            continue

    # STEP 4: If no code found, exit 
    if total_statements == 0:
        return {
            "status": "pass",
            "message": "No executable code found to evaluate assertions."
        }
    
    # STEP 5: Compute percentage and pass/fail status 
    percentage = (total_asserts / total_statements) * 100 
    status = "pass" if percentage >= 1.0 else "fail"

    if status == "pass":
        summary = "Some internal checks detected – good coding discipline."
        tip = "Keep using assert statements to validate assumptions, especially in critical functions and loops."
    else:
        summary = "No or very few assertion checks found."
        tip = "Adding assert statements can help catch bugs early by validating key conditions during execution."

    styled_summary = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{summary}</i></div>"
    styled_tip = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>Tip:</b> {tip}</div>"
    styled_note = (
        "<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>"
        "Note: This metric calculates the percentage of Python statements that are 'assert' checks. "
        "Projects with 1% or more are considered to use meaningful internal validation."
        "</i></div>"
    )

    message = (
        f"<div style='margin-left: 20px; font-size: 100%;'>"
        f"Assertions found: <b>{total_asserts}</b> out of <b>{total_statements}</b> statements "
        f"({percentage:.2f}%)</div>"
        f"{styled_summary}{styled_tip}{styled_note}"
    )

    return {
        "status": status,
        "message": message
    }