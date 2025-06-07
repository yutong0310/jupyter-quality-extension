import os
import nbformat

def count_python_loc(filepath):
    """Count non-blank, non-comment lines in a .py file"""
    count = 0
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1
    return count

def count_notebook_loc(filepath):
    """Count non-blank, non-comment lines in code cells of a .ipynb notebook"""
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "code":
                lines = cell.source.splitlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        count += 1
    return count

def run_project_loc():
    root_dir = os.getcwd()
    total_loc = 0
    excluded_dirs = {
        "venv", "__pycache__", ".ipynb_checkpoints", ".git",
        "bandit-report", "gitleaks-report", "jscpd-report"
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                if filename.endswith(".py"):
                    total_loc += count_python_loc(file_path)
                elif filename.endswith(".ipynb"):
                    total_loc += count_notebook_loc(file_path)
            except Exception:
                continue

    if total_loc < 1000:
        summary = "Small project size."
        tip = (
            "Focus on clarity and readability. Even small projects benefit from proper docstrings, meaningful variable names, "
            "and a simple modular structure to make future updates easier."
        )
    elif total_loc <= 5000:
        summary = "Medium project size."
        tip = (
            "As your project grows, organize related functions into reusable components or modules. "
            "Modularity supports testing, easier debugging, and future collaboration."
        )
    else:
        summary = "Large project – consider modularization."
        tip = (
            "Large codebases can quickly become hard to manage. Break logic into separate files or packages, "
            "use consistent documentation standards, and consider writing unit tests to ensure long-term maintainability."
        )

    styled_summary = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{summary}</i></div>"
    styled_tip = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>Tip:</b> {tip}</div>"
    styled_note = (
        "<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>"
        "Note: Only non-empty, non-comment lines in .py and .ipynb code cells are counted. "
        "Folders like <code>venv</code> or <code>__pycache__</code> are excluded."
        "</i></div>"
    )
    styled_loc = f"<div style='margin-left: 20px; color: black; font-size: 100%;'>{total_loc} lines of code in the project</div>"
    message = f"{styled_loc}{styled_summary}{styled_tip}{styled_note}"

    return {
        "status": "pass",
        "loc": total_loc,
        "message": message
    }

def run_loc_per_target(target_path):
    """
    Calculates non-empty lines of code for each .py file under the user-specified target path.

    Args:
        target_path (str): Path to file or folder.

    Returns:
        dict: { filepath: lines_of_code }
    """
    loc_per_file = {}

    if os.path.isfile(target_path) and target_path.endswith(".py"):
        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                loc = sum(1 for line in f if line.strip())
                loc_per_file[target_path] = loc
        except Exception:
            loc_per_file[target_path] = "Unreadable file."
    
    elif os.path.isdir(target_path):
        for dirpath, dirnames, filenames in os.walk(target_path):
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            loc = sum(1 for line in f if line.strip())
                            loc_per_file[file_path] = loc 
                    except Exception:
                        loc_per_file[file_path] = "Unreadable file."
    
    else:
        loc_per_file[target_path] = "Invalid file or folder."

    return loc_per_file