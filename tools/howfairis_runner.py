import subprocess

def run_howfairis_license_check(github_url):
    """
    Executes the howfairis CLI tool on the provided GitHub URL.
    Returns the full raw CLI output with status flag and explanatory notes.
    """

    try:
        # Prepare reusable UI blocks
        styled_summary = (
            "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
            "<i>This FAIR assessment checks your repository against 5 best practices from "
            "<a href='https://fair-software.eu/recommendations/checklist' target='_blank'>fair-software.eu</a>: "
            "open repository, license file, registry presence (e.g., PyPI or Zenodo), citation metadata, and a FAIR checklist badge in the README.</i>"
            "</div>"
        )

        styled_tip = (
            "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
            "<b>Tip:</b> To improve FAIR compliance, make sure your repository is public, includes a license, and optionally "
            "adds a <code>CITATION.cff</code> file or publishes the software to a registry like PyPI. "
            "Adding the FAIR checklist badge to your <code>README.md</code> shows commitment to good research software practices."
            "</div>"
        )

        # Run howfairis
        result = subprocess.run(
            ["howfairis", github_url],
            capture_output=True,
            text=True,
            timeout=20
        )

        # formatted_output = (
        #     "<div style='margin-left: 20px; font-family: monospace; font-size: 90%; "
        #     "white-space: pre-wrap; color: black;'>"
        #     f"{(result.stderr or result.stdout).strip()}"
        #     "</div>"
        # )

        raw_lines = (result.stderr or result.stdout).strip().splitlines()

        formatted_output = "<div style='margin-left: 20px; font-size: 90%; color: gray;'>"
        for line in raw_lines:
            # Make sure the line is safely escaped for HTML
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            formatted_output += f"<div style='font-family: monospace; white-space: pre;'>{safe_line}</div>"
        formatted_output += "</div>"

        return {
            "status": "pass" if result.returncode == 0 else "fail",
            "message": formatted_output + styled_summary + styled_tip
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"Exception while running howfairis: {str(e)}"
        }
