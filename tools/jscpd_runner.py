import os
import subprocess
import json

def get_filtered_python_files(root_path):
    """
    Recursively collects all .py files under root_path, excluding irrelevant dirs.
    Returns a list of file paths to scan.
    """
    excluded_dirs = {
        "venv", "env", "__pycache__", ".git", ".hg", ".svn",
        ".ipynb_checkpoints", ".mypy_cache", ".pytest_cache",
        "build", "dist", ".tox", ".nox", "site-packages",
        ".idea", ".vscode", ".DS_Store", "__pypackages__"
    }

    py_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        for file in filenames:
            if file.endswith(".py"):
                py_files.append(os.path.join(dirpath, file))
    return py_files

def run_jscpd_code_duplication(path):
    """
    Runs jscpd on the given path (file or folder) to detect code duplication.
    Parses the JSON report and returns duplication percentage. 

    Args:
        path (str): Path to a Python file or folder. 

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'percentage': float,
            'message': str
        }
    """

    # Step 1: Validate path exists
    if not os.path.exists(path):
        return {
            "status": "fail",
            "message": f"Path does not exist: {path}"
        }
    
    # Step 2: Set output directory for the jscpd report
    # It defines where jscpd will save the JSON output report (which contains the code duplication results).
    # This builds the full path to the report file: ./jscpd-report/jscpd-report.json
    # This is where code later looks to read back the analysis results. 
    output_dir = "./jscpd-report"
    report_file = os.path.join(output_dir, "jscpd-report.json")

    try:

        files_to_scan = get_filtered_python_files(path)
        if not files_to_scan:
            return {
                "status": "pass",
                "message": "No Python files found for duplication analysis."
            }

        # Step 3: Run jscpd using subprocess
        subprocess.run(
            [
                "jscpd",
                "--min-lines", "5",              # Minimum lines to consider duplication
                "--reporters", "json",           # Output format
                "--output", output_dir,          # Output directory
                *files_to_scan                   # File or folder to scan
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Step 4: Ensure report file was generated
        if not os.path.isfile(report_file):
            return {
                "status": "fail",
                "message": "jscpd report not found. Analysis may have failed."
            }
        
        # Step 5: Load JSON results
        with open(report_file, "r", encoding="utf-8") as f:
            # Parse the JSON content from the file and load it into a Python dictionary
            data = json.load(f)

        # Step 6: Extract total and duplicated line counts
        stats = data.get("statistics", {}).get("total", {})
        duplicated = stats.get("duplicatedLines", 0)
        total = stats.get("lines", 0)

        # Step 7: Calculate percentage duplicated
        percentage = (duplicated / total * 100) if total > 0 else 0

        # Determine severity and create styled explanation
        if percentage < 10:
            status = "pass"
            note = "Low duplication – clean code."
            tip = "Your notebook has low redundancy, which enhances maintainability and readability. Continue using helper functions and avoiding repeated code blocks."
        elif percentage < 20:
            status = "pass"
            note = "Moderate duplication – could be improved."
            tip = "Some code duplication exists. Consider refactoring shared logic into reusable functions to improve structure."
        else:
            status = "fail"
            note = "High duplication – code should be refactored."
            tip = "Significant repetition detected. Break down repeated blocks, modularize logic, and avoid copy-paste coding practices."

        styled_note = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{note}</i></div>"
        styled_tip = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>Tip:</b> {tip}</div>"
        legend = (
            "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
            "<i>Note: A duplication rate under 10% is considered good. Over 20% is typically problematic in maintainability.</i>"
            "</div>"
        )

        styled_topline = (
            f"<div style='margin-left: 20px; font-size: 100%;'>"
            f"Code Duplication Percentage: <b>{duplicated}</b> / <b>{total}</b> "
            f"({percentage:.2f}%)</div>"
        )

        message = f"{styled_topline}{styled_note}{styled_tip}{legend}"

        return {
            "status": status,
            "percentage": percentage,
            "duplicated_lines": duplicated,
            "total_lines": total,
            "message": message
        }
    
    except subprocess.CalledProcessError as e:
        return {
            "status": "fail",
            "message": f"jscpd error: {e.stderr.strip()}"
        }
    
    except Exception as e:
        return {
            "status": "fail",
            "message": f"Unexpected error while running jscpd: {str(e)}"
        }

# !!! This is to test clone detection 
def run_gitleaks_secret_scan():
    """
    Runs Gitleaks on the current project directory (cwd).
    Returns a dictionary formatted for display under "Project-Level Results".
    """
    try:
        # Use current working directory as project root
        root_path = os.getcwd()
        report_dir = os.path.join(root_path, "gitleaks-report")
        os.makedirs(report_dir, exist_ok=True)

        report_path = os.path.join(report_dir, "gitleaks_report.json")

        # Run Gitleaks
        result = subprocess.run(
            ["gitleaks", "detect", "--source", root_path,
             "--report-format", "json", "--report-path", report_path],
            capture_output=True,
            text=True,
            check=False
        )

        # If gitleaks fails (not 0 or 1), return the error
        if result.returncode not in [0, 1]:
            return {
                "status": "fail",
                "message": f"Gitleaks execution error: {result.stderr.strip()}"
            }

        # Load the report
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                findings = json.load(f)

            if findings:
                messages = [" Potential credentials found:"]
                for item in findings:
                    file = item.get("file", "")
                    secret = item.get("rule", "Secret")
                    line = item.get("line", "?")
                    messages.append(f"• `{secret}` in `{file}` (line {line})")

                return {
                    "status": "fail",
                    "message": "\n".join(messages)
                }
            else:
                return {
                    "status": "pass",
                    "message": "✓ No leaked credentials found."
                }

        return {
            "status": "fail",
            "message": "No Gitleaks report was generated."
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"Exception during Gitleaks scan: {str(e)}"
        }
