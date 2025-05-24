import subprocess
import os
import json

def run_bandit_security_scan():
    """
    Run Bandit on all user-written source files (excluding venv, __pycache__, etc)
    and summarize HIGH/MEDIUM severity issues.

    Returns:
        dict: A formatted project-level scan result with severity-based filtering.
    """

    # ---------------------------------------
    # STEP 1: Dynamically find user-written code folders
    # ---------------------------------------

    # Directories to ignore
    ignored_dirs = {"venv", ".git", "__pycache__", ".ipynb_checkpoints", "bandit-report", ".mypy_cache"}

    # Collect top-level folders/files to include
    current_dir = os.getcwd()
    targets = []

    for item in os.listdir(current_dir):
        # Full path
        path = os.path.join(current_dir, item)

        # Skip unwanted system/virtual dirs
        if item in ignored_dirs:
            continue

        # Add if it's a Python file or directory
        if os.path.isdir(path) or (os.path.isfile(path) and path.endswith(".py")):
            targets.append(item)

    if not targets:
        return {
            "status": "fail",
            "message": "No user code found to scan. Project directory is empty or only contains ignored folders."
        }

    # ---------------------------------------
    # STEP 2: Run Bandit
    # ---------------------------------------

    output_dir = "bandit-report"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "bandit_report.json")

    try:
        subprocess.run(
            ["bandit", "-r", *targets, "-f", "json", "-o", report_path],
            check=False,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        return {
            "status": "fail",
            "message": f"Bandit scan failed.\n\n{e.stderr}"
        }

    # ---------------------------------------
    # STEP 3: Parse and Filter Report
    # ---------------------------------------

    if not os.path.exists(report_path):
        return {
            "status": "fail",
            "message": "Bandit report was not generated."
        }

    with open(report_path, "r") as f:
        data = json.load(f)

    results = data.get("results", [])

    # Only show MEDIUM and HIGH severity issues
    # filtered = [r for r in results if r.get("issue_severity") in {"MEDIUM", "HIGH", "LOW"}]

    # Sort all results by severity: HIGH → MEDIUM → LOW
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    filtered = sorted(results, key=lambda r: severity_order.get(r.get("issue_severity", "LOW"), 3))

    if not filtered:
        return {
            "status": "pass",
            "message": "✓ No medium or high-severity security vulnerabilities found."
        }

    # ---------------------------------------
    # STEP 4: Summarize Clearly
    # ---------------------------------------

    messages = []
    for issue in filtered:
        file = issue.get("filename")
        line = issue.get("line_number")
        severity = issue.get("issue_severity")
        msg = issue.get("issue_text")
        rule = issue.get("test_id")

        messages.append(f"• [{severity}] {msg} (File: `{file}`, Line: {line}, Rule: {rule})")

    return {
        "status": "fail",
        # "message": "⚠️ Medium or high-severity vulnerabilities detected:\n\n" + "\n".join(messages)
        "message": "! Bandit found potential security issues:\n\n" + "\n".join(messages)
    }
