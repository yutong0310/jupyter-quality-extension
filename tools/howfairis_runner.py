import subprocess

def run_howfairis_license_check(github_url):
    """
    Executes the howfairis CLI tool on the provided GitHub URL.
    Returns the full raw CLI output, line by line.
    """

    try:
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

        # Return raw lines (no markdown block formatting!)
        return {
            "status": "pass",
            "message": result.stdout.strip()  # clean multiline string
        }

    except Exception as e:
        return {
            "status": "fail",
            "message": f"Exception while running howfairis: {str(e)}"
        }
