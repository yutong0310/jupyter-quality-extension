import os  
from IPython.display import display, HTML, Markdown
from tools.pylint_runner import run_pylint_code_smell  
from tools.radon_runner import run_radon_maintainability_index
from tools.radon_runner import run_radon_cyclomatic_complexity
from tools.radon_runner import run_radon_comment_density
from tools.jscpd_runner import run_jscpd_code_duplication
from tools.loc_counter import run_project_loc
from tools.assertion_counter import run_assertion_percentage
from tools.howfairis_runner import run_howfairis_license_check
from tools.gitleaks_runner import run_gitleaks_secret_scan
from tools.bandit_runner import run_bandit_security_scan
from tools.dependency_checker import run_dependency_check
from evaluation.notebook_converter import convert_notebooks_in_dir

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
    results = {}

    # Convert notebooks if the target is a directory or an .ipynb file
    if os.path.isdir(path):
        convert_notebooks_in_dir(path)
        # Collect all Python files (converted or original)
        python_files = []
        for root, dirs, files in os.walk(path):

            excluded_dirs = {
                    "venv", "env", "__pycache__", ".git", ".hg", ".svn",
                    ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache",
                    "build", "dist", ".tox", ".nox", "site-packages",
                    ".idea", ".vscode", ".DS_Store", "__pypackages__",
                    "jscpd-report", "bandit-report", "gitleaks-report"
            }
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

    elif path.endswith(".ipynb"):
        # Convert this single notebook to Python
        converted_path = convert_notebooks_in_dir(path)
        python_files = [converted_path] if converted_path else []
    
    elif path.endswith(".py"):
        python_files = [path]
    
    else:
        raise ValueError("Invalid target path. Must be a Python file, notebook, or directory.")
    
    results["Project-Level Results"] = {}

    if any(m in metrics for m in ["Presence of License", "No Leaked Private Credentials", "Security Vulnerabilities"]):
        results["Project-Level Results"]["FAIR Assessment (howfairis)"] = run_howfairis_license_check(github_url)
        results["Project-Level Results"]["-----divider-1-----"] = {"status": "pass", "message": ""}
        results["Project-Level Results"]["Leaked Secrets Scan (Gitleaks)"] = run_gitleaks_secret_scan(path)
        results["Project-Level Results"]["-----divider-2-----"] = {"status": "pass", "message": ""}
        results["Project-Level Results"]["Security Vulnerability Scan (Bandit)"] = run_bandit_security_scan(path)

    if "Dependency Management" in metrics:
        results["Project-Level Results"]["Dependency Management"] = run_dependency_check(path)
    
    if "Software Size (LoC)" in metrics:
        results["Project-Level Results"]["Software Size (LoC)"] = run_project_loc(path)

    if "Code Duplication" in metrics:
        results["Project-Level Results"]["Code Duplication"] = run_jscpd_code_duplication(path)

    if "Percentage of Assertions" in metrics: 
        results["Project-Level Results"]["Percentage of Assertions"] = run_assertion_percentage(path)

    # === File-level metrics ===
    for file in python_files:
        file_results = {}
        for metric in metrics:
            if metric in [
                "Code Smells", "Maintainability Index", "Cyclomatic Complexity",
                "Comment Density"
            ]:
                if metric == "Code Smells":
                    file_results[metric] = run_pylint_code_smell(file)

                elif metric == "Maintainability Index":
                    file_results[metric] = run_radon_maintainability_index(file)

                elif metric == "Cyclomatic Complexity":
                    file_results[metric] = run_radon_cyclomatic_complexity(file)

                elif metric == "Comment Density":
                    file_results[metric] = run_radon_comment_density(file)
                
            results[file] = file_results

    return results
    
# def evaluate_metrics(metrics, path, github_url=None):

#     results = {}  # Final output dictionary containing all scanned file results
#     files = []    # A list to hold all .py files we find

#     # Determine whether to scan files or not
#     scanning_files = any(
#         metric not in ["Presence of License"] for metric in metrics
#     )

#     # PART A – Project-level metric (e.g., license)
#     results["Project-Level Results"] = {}

#     if any(m in metrics for m in ["Presence of License", "No Leaked Private Credentials", "Security Vulnerabilities"]):
#         results["Project-Level Results"]["FAIR Assessment (howfairis)"] = run_howfairis_license_check(github_url)
#         results["Project-Level Results"]["-----divider-1-----"] = {"status": "pass", "message": ""}
#         results["Project-Level Results"]["Leaked Secrets Scan (Gitleaks)"] = run_gitleaks_secret_scan()
#         results["Project-Level Results"]["-----divider-2-----"] = {"status": "pass", "message": ""}
#         results["Project-Level Results"]["Security Vulnerability Scan (Bandit)"] = run_bandit_security_scan()
    
#     if "Dependency Management" in metrics:
#         results["Project-Level Results"]["Dependency Management"] = run_dependency_check(path)
    
#     if "Software Size (LoC)" in metrics:
#         results["Project-Level Results"]["Software Size (LoC)"] = run_project_loc(path)

#     if "Code Duplication" in metrics:
#         results["Project-Level Results"]["Code Duplication"] = run_jscpd_code_duplication(path)

#     if "Percentage of Assertions" in metrics: 
#         results["Project-Level Results"]["Percentage of Assertions"] = run_assertion_percentage(path)

#     # PART B – File-level metrics
#     if scanning_files:

#         # Convert any .ipynb notebooks into .py before continuing
#         convert_notebooks_in_dir(path)

#         # STEP 1: Determine whether path is a file or folder
#         # Case 1: User entered a single .py file
#         if os.path.isfile(path) and path.endswith(".py"):
#             files.append(path)

#         # (NEW) Case 2: User entered a single .ipynb notebook
#         elif os.path.isfile(path) and path.endswith(".ipynb") and ".ipynb_checkpoints" not in path:
#             py_path = path.replace(".ipynb", ".py")
#             if os.path.exists(py_path):
#                 files.append(py_path)
#             else:
#                 results["ERROR"] = {
#                     "Notebook Conversion Failed": {
#                         "status": "fail",
#                         "message": f"Notebook has not converted to Python file: {path}"
#                     }
#                 }
#                 return results

#         # Case 3: User entered a folder → walk recursively through subfolders
#         elif os.path.isdir(path):
#             # os.walk() recursively traverses a directory tree. It yields a tuple (root, dirs, files):
#             # - root: current folder path.  - dirs: list of subfolders.  - files: list of files in this folder
#             for root, dirs, filenames in os.walk(path):

#                 excluded_dirs = {
#                     "venv", "env", "__pycache__", ".git", ".hg", ".svn",
#                     ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache",
#                     "build", "dist", ".tox", ".nox", "site-packages",
#                     ".idea", ".vscode", ".DS_Store", "__pypackages__",
#                     "jscpd-report", "bandit-report", "gitleaks-report"
#                 }
#                 dirs[:] = [d for d in dirs if d not in excluded_dirs]

#                 for filename in filenames:
#                     if filename.endswith(".py") and filename != "__init__.py":
#                         full_path = os.path.join(root, filename)
#                         files.append(full_path)

#         # Case 3: Input path is invalid (not a file or folder)
#         else:
#             results["ERROR"] = {
#                 "Input Path": {
#                     "status": "fail",
#                     "message": "Path is not a valid Python file or folder."
#                 }
#             }
#             return results

#         # STEP 2: If no .py files were found, return a failure message
#         if not files:
#             results["ERROR"] = {
#                 "No Python Files Found": {
#                     "status": "fail",
#                     "message": f"No .py files found under path: {path}"
#                 }
#             }
#             return results

#         # STEP 3: Evaluate all selected metrics for each .py file found
#         for file in files:
#             file_results = {}  # Dictionary to hold results for one file

#             for metric in metrics:

#                 if metric == "Presence of License":
#                     continue  

#                 if metric == "Cognitive Complexity":
#                     continue

#                 if metric == "Dependency Management":
#                     continue

#                 if metric == "Code Smells":
#                     file_results[metric] = run_pylint_code_smell(file)

#                 elif metric == "Maintainability Index":
#                     file_results[metric] = run_radon_maintainability_index(file)

#                 elif metric == "Cyclomatic Complexity":
#                     file_results[metric] = run_radon_cyclomatic_complexity(file)

#                 elif metric == "Comment Density":
#                     file_results[metric] = run_radon_comment_density(file)

#                 elif metric == "Code Duplication":
#                     continue

#                 elif metric == "Technical Debt":
#                     continue
            
#                 elif metric == "Software Size (LoC)":
#                     continue
                
#                 elif metric == "Percentage of Assertions":
#                     continue

#                 else:
#                     file_results[metric] = {
#                         "status": "pass",
#                         "message": "Simulated result"
#                     }

#             results[file] = file_results

#     return results