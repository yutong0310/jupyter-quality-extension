import os  
from tools.pylint_runner import run_pylint_code_smell  
from tools.radon_runner import run_radon_maintainability_index
from tools.radon_runner import run_radon_cyclomatic_complexity
from tools.radon_runner import run_radon_comment_density
from tools.jscpd_runner import run_jscpd_code_duplication
from tools.loc_counter import run_project_loc
from tools.loc_counter import run_loc_per_target
from tools.assertion_counter import run_assertion_percentage
from tools.unit_test_checker import run_unit_test_detection
from tools.howfairis_runner import run_howfairis_license_check

def evaluate_metrics(metrics, path):
    """
    Evaluates selected software quality metrics on a given Python file or folder.

    Args:
        metrics (list): List of metric names selected by the user (e.g., ["Code Smells", "Maintainability Index"])
        path (str): Path to a file or folder provided by the user.

    Returns:
        dict: A nested dictionary with the structure:
            {
                "file1.py": {
                    "Metric A": {status: ..., message: ...},
                    "Metric B": {...}
                },
                "file2.py": { ... }
            }
    """

    results = {}  # Final output dictionary containing all scanned file results
    files = []    # A list to hold all .py files we find

    # ------------------------------------------------------------
    # STEP 1: Determine whether path is a file or folder
    # ------------------------------------------------------------

    # Case 1: User entered a single .py file
    if os.path.isfile(path) and path.endswith(".py"):
        files.append(path)

    # Case 2: User entered a folder → walk recursively through subfolders
    elif os.path.isdir(path):
        # os.walk() recursively traverses a directory tree
        # It yields a tuple (root, dirs, files) for every directory it visits:
        # - root: current folder path
        # - dirs: list of subfolders
        # - files: list of files in this folder
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith(".py"):
                    # Construct full file path and add it to our list
                    full_path = os.path.join(root, filename)
                    files.append(full_path)

    # Case 3: Input path is invalid (not a file or folder)
    else:
        return {
            "ERROR": {
                "Input Path": {
                    "status": "fail",
                    "message": "Path is not a valid Python file or folder."
                }
            }
        }

    # ------------------------------------------------------------
    # STEP 2: If no .py files were found, return a failure message
    # ------------------------------------------------------------
    if not files:
        return {
            "ERROR": {
                "No Python Files Found": {
                    "status": "fail",
                    "message": f"No .py files found under path: {path}"
                }
            }
        }

    # ------------------------------------------------------------
    # STEP 3: Evaluate all selected metrics for each .py file found
    # ------------------------------------------------------------

    for file in files:
        file_results = {}  # Dictionary to hold results for one file

        for metric in metrics:
            # 🔎 Match the metric to its corresponding analysis tool
            if metric == "Code Smells":
                file_results[metric] = run_pylint_code_smell(file)

            elif metric == "Maintainability Index":
                file_results[metric] = run_radon_maintainability_index(file)

            elif metric == "Cyclomatic Complexity":
                file_results[metric] = run_radon_cyclomatic_complexity(file)

            elif metric == "Code Duplication":
                # Run jscpd per folder
                file_results[metric] = run_jscpd_code_duplication(os.path.dirname(file))

            elif metric == "Comment Density":
                file_results[metric] = run_radon_comment_density(file)

            elif metric == "Software Size (LoC)":
                # Always calculate full project size
                project_loc = run_project_loc()

                # Also calculate lines of code per file under user input target_path
                file_locs = run_loc_per_target(path)

                file_list_text = "  \n".join([f"    • {os.path.basename(fname)}: {loc} lines" for fname, loc in file_locs.items()])

                file_results[metric] = {
                    "status": "pass",
                    "message": f"{project_loc['message']}\n\n{file_list_text}"
                }
            
            elif metric == "Percentage of Assertions":
                file_results[metric] = run_assertion_percentage(path)

            elif metric == "Unit Tests":
                file_results[metric] = run_unit_test_detection(path)

            elif metric == "Presence of License":
                # Always use the Jupyter root directory regardless of user selection
                root_path = os.getcwd()
                file_results[metric] = run_howfairis_license_check(root_path)

            else:
                # Placeholder for future metrics (e.g., Test Success Rate, Security)
                file_results[metric] = {
                    "status": "pass",
                    "message": "Simulated result"
                }

        # Store the results for this file in the overall result dictionary
        results[file] = file_results

    return results
