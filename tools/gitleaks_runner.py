import subprocess
import os
import json

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
                messages = ["🚨 Potential credentials found:"]
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
                    "message": "✅ No leaked credentials found."
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
