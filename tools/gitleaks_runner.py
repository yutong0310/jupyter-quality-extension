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
                
                styled_summary = "<div style='margin-left: 20px; color: red;'>! Potential credentials found in the code:</div>"

                styled_findings = ""
                for item in findings:
                    file = item.get("File", "")
                    secret = item.get("RuleID", "Secret")
                    line = item.get("Line", "?")
                    styled_findings += f"<div style='margin-left: 20px; font-size: 90%; font-family: monospace;'>• {secret} in {file} (line {line})</div>"

                styled_tip = (
                    "<div style='margin-left: 20px; color: gray; font-size: 90%;'>" 
                    "<b>Tip:</b> If any secrets were exposed, revoke and regenerate them immediately through your service provider. To prevent future leaks, avoid hardcoding credentials and store them in environment variables or separate config files excluded from version control."
                    "</div>"
                )
                
                legend = (
                    "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
                    "<i>Note: This scan checks for accidentally committed secrets such as API keys, tokens, and passwords. Keeping them out of code reduces risk and improves security practices.</i>"
                    "</div>"
                )

                return {
                    "status": "fail",
                    # "message": "\n".join(messages) + styled_tip + legend
                    "message": styled_summary + styled_findings + styled_tip + legend
                }
            
            else:

                styled_note = "<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>No secrets detected – your code is clean and safe.</i></div>"
                styled_tip = "<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>Tip:</b> Keep sensitive keys, tokens, and credentials out of your codebase. Use environment variables or secret managers for secure handling.</div>"
                legend = "<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>Note: Gitleaks scans for hardcoded secrets like API keys, credentials, and tokens across your repository history.</i></div>"
                styled_summary = "<div style='margin-left: 20px;'>✓ No leaked credentials found.</div>"

                return {
                    "status": "pass",
                    # "message": "✓ No leaked credentials found." + styled_note + styled_tip + legend
                    "message": styled_summary + styled_note + styled_tip + legend
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
