import subprocess
import re 

def run_howfairis_license_check(github_url):
    """
    Executes the howfairis CLI tool on the provided GitHub URL.
    Returns the full raw CLI output with status flag and explanatory notes.
    """

    try:
        # Prepare reusable UI blocks
        styled_summary = (
            "<div style='margin-left: 20px; color: gray; font-size: 90%;'>"
            "<br><i>This FAIR assessment checks your repository against 5 best practices from "
            "<a href='https://fair-software.eu/recommendations/checklist' target='_blank'>fair-software.eu</a>: "
            "open repository, license file, registry presence (e.g., PyPI), citation metadata, and a FAIR checklist badge in the README.</i>"
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

        # score_line = next((line for line in raw_lines if "Calculated compliance" in line), "")
        # score_str = "".join(c for c in score_line if c in "●○").strip()
        # num_filled = score_str.count("●")

        # if num_filled <= 1:
        #     badge_color = "#e05d44"   # Red
        # elif num_filled <= 3:
        #     badge_color = "#fe7d37"   # Orange
        # elif num_filled == 4:
        #     badge_color = "#dfb317"   # Yellow
        # else:
        #     badge_color = "#97ca00"   # Green

        # styled_score = (
        #     f"<div style='margin-left: 20px; font-size: 90%; font-family: monospace;'>"
        #     f"<span style='background-color: #444; color: white; padding: 2px 6px; border-radius: 3px;'>"
        #     f"fair-software.eu</span>"
        #     f"<span style='background-color: {badge_color}; color: white; padding: 2px 8px; "
        #     f"border-radius: 3px; margin-left: 5px;'>{score_str}</span>"
        #     f"<span style='color: gray; margin-left: 6px;'>(Score: {num_filled}/5)</span>"
        #     "</div>"
        # )

        formatted_output = "<div style='margin-left: 20px; font-size: 90%; color: gray;'>"
        
        for line in raw_lines:

            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            formatted_output += f"<div style='font-family: monospace; white-space: pre;'>{safe_line}</div>"
            
        formatted_output += "</div>"

        return {
            "status": "pass" if result.returncode == 0 else "fail",
            # "message": styled_score + formatted_output + styled_summary + styled_tip
            "message": formatted_output + styled_summary + styled_tip
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"Exception while running howfairis: {str(e)}"
        }
