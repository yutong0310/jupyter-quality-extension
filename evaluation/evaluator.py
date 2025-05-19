import os  
from IPython.display import display, HTML, Markdown
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
from tools.gitleaks_runner import run_gitleaks_secret_scan
from tools.bandit_runner import run_bandit_security_scan

# Maintenance metric overview section
def get_maintenance_metrics_status():
    return [
        ("Presence of License", "measured", "Automatically checked via howfairis."),
        ("Publicly Accessible Repository", "measured", "Automatically checked via howfairis."),
        ("Rich Metadata", "partial", "Note: Partially measured by howfairis. This checks presence of citation metadata only, not completeness or quality."),
        ("Documentation Quality", "partial", "Note: Partially measured by howfairis. This checks documentation by verifying citation metadata, but not how well-documented the code is."),
        ("User Satisfaction", "manual", "Not automatically measurable. This requires user surveys or interviews."),
        ("No Leaked Private Credentials", "measured", "Automatically checked via gitleaks."),
        ("Security Vulnerabilities", "measured", "Automatically checked via bandit.")
    ]

def display_maintenance_metric_overview():
    status_icon = {
        "measured": "✓",
        "partial": "~",
        "manual": "×"
    }

    display(HTML("<h4> Maintenance Metrics Being Checked:</h4><ul>"))

    for name, status, note in get_maintenance_metrics_status():
        icon = status_icon.get(status, "?")
        if status == "manual":
            label = "requires human evaluation"
        elif status == "partial":
            label = "partially measured"
        else:
            label = "measured"
        
        display(HTML(f"<li>{icon} <b>{name}</b> ({label})</li>"))
        display(HTML(f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{note}</i></div><br>"))

    display(HTML("</ul>"))
# -------------------------------

def evaluate_metrics(metrics, path, github_url=None):
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

    # Determine whether to scan files or not
    scanning_files = any(
        metric not in ["Presence of License"] for metric in metrics
    )

    # ---------------------------------------------
    # PART A – Project-level metric (e.g., license)
    # ---------------------------------------------
    if any(m in metrics for m in ["Presence of License", "No Leaked Private Credentials", "Security Vulnerabilities"]):
        results["Project-Level Results"] = {
            "FAIR Assessment (howfairis)": run_howfairis_license_check(github_url),
            "-----divider-1-----": {"status": "pass", "message": ""},
            "Leaked Secrets Scan (Gitleaks)": run_gitleaks_secret_scan(),
            "-----divider-2-----": {"status": "pass", "message": ""},
            "Security Vulnerability Scan (Bandit)": run_bandit_security_scan()
        }

    # ---------------------------------------------
    # PART B – File-level metrics
    # ---------------------------------------------
    if scanning_files:

        # ------------------------------------------------------------
        # STEP 1: Determine whether path is a file or folder
        # ------------------------------------------------------------

        # Case 1: User entered a single .py file
        if os.path.isfile(path) and path.endswith(".py"):
            files.append(path)

        # Case 2: User entered a folder → walk recursively through subfolders
        elif os.path.isdir(path):
            # os.walk() recursively traverses a directory tree. It yields a tuple (root, dirs, files) for every directory it visits:
            # - root: current folder path.  - dirs: list of subfolders.  - files: list of files in this folder
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(".py"):
                        # Construct full file path and add it to our list
                        full_path = os.path.join(root, filename)
                        files.append(full_path)

        # Case 3: Input path is invalid (not a file or folder)
        else:
            results["ERROR"] = {
                "Input Path": {
                    "status": "fail",
                    "message": "Path is not a valid Python file or folder."
                }
            }
            return results

        # ------------------------------------------------------------
        # STEP 2: If no .py files were found, return a failure message
        # ------------------------------------------------------------
        if not files:
            results["ERROR"] = {
                "No Python Files Found": {
                    "status": "fail",
                    "message": f"No .py files found under path: {path}"
                }
            }
            return results

        # ------------------------------------------------------------
        # STEP 3: Evaluate all selected metrics for each .py file found
        # ------------------------------------------------------------

        for file in files:
            file_results = {}  # Dictionary to hold results for one file

            for metric in metrics:

                if metric == "Presence of License":
                    continue  

                # Match the metric to its corresponding analysis tool
                if metric == "Code Smells":
                    result = run_pylint_code_smell(file)
                    result["message"] = "<br>".join(result["message"])
                    file_results[metric] = result

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

                    project_loc = run_project_loc() # Always calculate full project size
                    file_locs = run_loc_per_target(path) # Also calculate lines of code per file under user input target_path

                    file_list_text = "  \n".join([f"    • {os.path.basename(fname)}: {loc} lines" for fname, loc in file_locs.items()])

                    file_results[metric] = {
                        "status": "pass",
                        "message": f"{project_loc['message']}\n\n{file_list_text}"
                    }
                
                elif metric == "Percentage of Assertions":
                    file_results[metric] = run_assertion_percentage(path)

                elif metric == "Unit Tests":
                    file_results[metric] = run_unit_test_detection(path)

                else:
                    # Placeholder for future metrics (e.g., Test Success Rate, Security)
                    file_results[metric] = {
                        "status": "pass",
                        "message": "Simulated result"
                    }

            # Store the results for this file in the overall result dictionary
            results[file] = file_results

    return results
