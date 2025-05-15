import subprocess

def run_howfairis_license_check(github_url):
    """
    Executes the howfairis CLI tool on the provided GitHub URL.
    Returns the full raw CLI output with status flag.
    """

    try:
        # Run howfairis as subprocess and capture all output
        result = subprocess.run(
            ["howfairis", github_url],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode != 0:
            return {
                "status": "fail",
                "message": result.stderr.strip() or result.stdout.strip()
            }

        # Show full raw output from howfairis
        return {
            "status": "pass",
            "message": f"```\n{result.stdout.strip()}\n```"
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"Exception while running howfairis: {str(e)}"
        }
