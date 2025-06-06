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

    # STEP 1: Identify valid target folders/files
    ignored_dirs = {"venv", ".git", "__pycache__", ".ipynb_checkpoints", "bandit-report", ".mypy_cache"}
    current_dir = os.getcwd()
    targets = []

    for item in os.listdir(current_dir):
        path = os.path.join(current_dir, item)
        if item in ignored_dirs:
            continue
        if os.path.isdir(path) or (os.path.isfile(path) and path.endswith(".py")):
            targets.append(item)

    if not targets:
        return {
            "status": "fail",
            "message": "No user code found to scan. Project directory is empty or only contains ignored folders."
        }

    # STEP 2: Run Bandit and store results in a JSON file
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

    if not os.path.exists(report_path):
        return {
            "status": "fail",
            "message": "Bandit report was not generated."
        }

    # STEP 3: Parse and filter MEDIUM/HIGH issues
    with open(report_path, "r") as f:
        data = json.load(f)

    all_results = data.get("results", [])
    severity_to_show = {"LOW", "MEDIUM", "HIGH"}
    filtered = [r for r in all_results if r.get("issue_severity") in severity_to_show]
    filtered = sorted(filtered, key=lambda r: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(r.get("issue_severity"), 3))

    has_medium_or_high = any(r["issue_severity"] in {"MEDIUM", "HIGH"} for r in filtered)

    # STEP 4: Generate styled UI output
    styled_note = (
        "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
        "<i>Note: Bandit detects security vulnerabilities in Python code using static analysis. "
        "Each issue is ranked as LOW, MEDIUM, or HIGH based on severity.</i></div>"
    )
    styled_tip = (
        "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
        "<b>Tip:</b> Focus on resolving MEDIUM and HIGH severity issues first. "
        "Watch for risky constructs like subprocess calls, use of eval, or hardcoded secrets. "
        "Even LOW severity findings may require attention in sensitive applications.</div>"
    )

    if not has_medium_or_high:
        styled_summary = (
            "<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>No medium or high-severity risks detected, only low-severity suggestions shown below.</i></div>"
        )
        styled_header = (
            "<div style='margin-left: 20px;'>✓ No medium or high-severity security vulnerabilities found.</div>"
        )
        styled_results = "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
        for issue in filtered:
            file = issue.get("filename")
            line = issue.get("line_number")
            severity = issue.get("issue_severity")
            msg = issue.get("issue_text")
            rule = issue.get("test_id")
            styled_results += f"• [{severity}] {msg} (File: <code>{file}</code>, Line: {line}, Rule: {rule})<br>"
        styled_results += "</div>"
        return {
            "status": "pass",
            "message": styled_header + styled_summary + styled_results + styled_tip + styled_note
        }

    # At least one MEDIUM or HIGH issue → fail
    styled_header = (
        "<div style='margin-left: 20px; color: red;'>✗ Bandit found potential security issues:</div>"
    )
    styled_summary = (
        "<div style='margin-left: 20px;'><i>Medium or high-severity risks were detected — review needed.</i></div>"
    )
    styled_results = "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
    for issue in filtered:
        file = issue.get("filename")
        line = issue.get("line_number")
        severity = issue.get("issue_severity")
        msg = issue.get("issue_text")
        rule = issue.get("test_id")
        styled_results += f"• [{severity}] {msg} (File: <code>{file}</code>, Line: {line}, Rule: {rule})<br>"
    styled_results += "</div>"

    return {
        "status": "fail",
        "message": styled_header + styled_summary + styled_results + styled_note + styled_tip
    }