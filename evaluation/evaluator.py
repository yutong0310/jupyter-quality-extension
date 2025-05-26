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
from tools.modularity_checker import run_modularity_check
from tools.dependency_checker import run_dependency_check

# Development metric overview section
def get_development_metrics_status():
    return [
        ("Code Smells", "measured", "Automatically checked via pylint."),
        ("Maintainability Index", "measured", "Automatically checked via radon."),
        ("Cognitive Complexity", "manual", "Not automatically measurable. Requires human judgment to assess nested structures, logic flow, and mental overhead."),
        ("Cyclomatic Complexity", "measured", "Automatically checked via radon."),
        ("Code Duplication", "measured", "Automatically checked via jscpd."),
        ("Technical Debt", "partial", "Estimated indirectly using indicators like code smells (pylint), cyclomatic complexity (radon), code duplication (jscpd), and maintainability index (radon). These issues often lead to technical debt. While no standard tool calculates technical debt for research notebooks, this approximation gives insight into future refactoring."),
        ("Dependency Management", "partial", "Partially measured by checking whether required libraries are declared in requirements.txt and used in code. Helps detect missing or unused dependencies."),
        ("Comment Density", "measured", "Automatically checked via radon (raw analysis)."),
        ("Software Size (LoC)", "measured", "Automatically checked via custom script."),
        ("Percentage of Assertions", "measured", "Automatically checked via custom script.")
    ]

def display_development_metric_overview():
    status_icon = {
        "measured": "✓",
        "partial": "~",
        "manual": "×"
    }

    label_text = {
        "measured": "measured",
        "partial": "partially measured",
        "manual": "requires human evaluation"
    }

    display(HTML("<h4>Development Metrics Being Checked:</h4><ul>"))
    for name, status, explanation in get_development_metrics_status():
        icon = status_icon.get(status, "?")
        label = label_text.get(status, status)

        display(HTML(
            f"<li>{icon} <b>{name}</b> ({label})"
            f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{explanation}</i></div></li><br>"
        ))
    display(HTML("</ul>"))

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
    results["Project-Level Results"] = {}

    if any(m in metrics for m in ["Presence of License", "No Leaked Private Credentials", "Security Vulnerabilities"]):
        results["Project-Level Results"]["FAIR Assessment (howfairis)"] = run_howfairis_license_check(github_url)
        results["Project-Level Results"]["-----divider-1-----"] = {"status": "pass", "message": ""}
        results["Project-Level Results"]["Leaked Secrets Scan (Gitleaks)"] = run_gitleaks_secret_scan()
        results["Project-Level Results"]["-----divider-2-----"] = {"status": "pass", "message": ""}
        results["Project-Level Results"]["Security Vulnerability Scan (Bandit)"] = run_bandit_security_scan()

    
    # if "Modularity" in metrics:
    #    results["Project-Level Results"]["⚠️ Modularity (Structure Overview)"] = run_modularity_check(path)

    if "Dependency Management" in metrics:
        project_root = os.getcwd()
        results["Project-Level Results"]["Dependency Management"] = run_dependency_check(project_root)
    
    if "Software Size (LoC)" in metrics:
        results["Project-Level Results"]["Software Size (LoC)"] = run_project_loc()

    if "Code Duplication" in metrics:
        project_root = os.getcwd()
        results["Project-Level Results"]["Code Duplication"] = run_jscpd_code_duplication(project_root)

    if "Percentage of Assertions" in metrics:
        project_root = os.getcwd()
        results["Project-Level Results"]["Percentage of Assertions"] = run_assertion_percentage(project_root)

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
                    file_results[metric] = run_pylint_code_smell(file)

                elif metric == "Maintainability Index":
                    file_results[metric] = run_radon_maintainability_index(file)
                
                elif metric == "Cognitive Complexity":
                    continue

                elif metric == "Cyclomatic Complexity":
                    file_results[metric] = run_radon_cyclomatic_complexity(file)

                elif metric == "Code Duplication":
                    continue

                elif metric == "Technical Debt":
                    continue

                elif metric == "Dependency Management":
                    continue
                
                elif metric == "Comment Density":
                    file_results[metric] = run_radon_comment_density(file)

                elif metric == "Software Size (LoC)":
                    continue
                
                elif metric == "Percentage of Assertions":
                    continue

                # elif metric == "Unit Tests":
                #     file_results[metric] = run_unit_test_detection(path)

                else:
                    # Placeholder for future metrics 
                    file_results[metric] = {
                        "status": "pass",
                        "message": "Simulated result"
                    }

            # Store the results for this file in the overall result dictionary
            results[file] = file_results

    return results
