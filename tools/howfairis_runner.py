import subprocess
import os

def run_howfairis_license_check(path=None):
    """
    Run howfairis as a subprocess to check for license presence.
    
    Returns:
        dict: {
            "status": "pass" or "fail",
            "message": str
        }
    """
    project_root = os.getcwd() 

    try:
        result = subprocess.run(
            ["howfairis", project_root],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True 
        )

        output = result.stdout.lower()

        if "has_license: true" in output:
            return {
                "status": "pass",
                "message": "License file detected in project root."
            }
        else:
            return {
                "status": "fail",
                "message": "No license file found in the project root."
            }
    
    except subprocess.CalledProcessError as e:
        return {
            "status": "fail",
            "message": f"howfairis CLI failed: {e.stderr.strip()}"
        }