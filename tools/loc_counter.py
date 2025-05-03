import os

def run_project_loc():
    """
    Calculates the total number of non-empty lines of code (LoC) in all Python (.py) files
    across the entire project directory (excluding irrelevant folders like venv).

    Returns:
        dict: {
            "status": "pass",
            "loc": total line count,
            "message": readable summary
        }
    """

    root_dir = os.getcwd() # Get the current working directory (assumed as project root)
    total_loc = 0 # This will store the cumulative lines of code

    # os.walk() recursively traverses all directories from root_dir
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip any folders we don't want to include (like virtualenvs, caches)
        if 'venv' in dirpath or '__pycache__' in dirpath:
            continue

        for filename in filenames:
            if filename.endswith(".py"):  # Only count Python files
                file_path = os.path.join(dirpath, filename)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    # Count lines that are not just whitespace
                    file_loc = sum(1 for line in f if line.strip())
                    total_loc += file_loc
            except Exception:
                    # Skip unreadable files
                    continue
    return {
        "status": "pass",
        "loc": total_loc,
        "message": f"Total non-empty lines of code in the project: {total_loc}"
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