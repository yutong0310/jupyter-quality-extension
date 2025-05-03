import subprocess  
import os  

def run_pylint_code_smell(filepath):
    """
    Runs pylint on the specified Python file to detect code smells,
    such as warnings, bad practices, or potential errors.

    Args:
        filepath (str): The path to the Python file to analyze.

    Returns:
        dict: A dictionary containing:
              - 'status': "pass" if no major issues were found, otherwise "fail"
              - 'message': A summary message or detailed error output
    """

    # STEP 1: Check if the specified file exists and is a valid file
    if not os.path.isfile(filepath):
        return {
            "status": "fail",
            "message": f"File not found: {filepath}"  
        }

    try:
        # STEP 2: Run pylint on the file using subprocess
        output = subprocess.check_output(
            ['pylint', filepath],          # Command to run pylint on the file
            stderr=subprocess.STDOUT,      # Redirect standard error to standard output
            text=True                      # Return output as a string instead of bytes
        )

        # If pylint runs successfully (exit code 0), consider it a pass
        return {
            "status": "pass",
            "message": "No major code smells found."  
        }

    except subprocess.CalledProcessError as e:
        # pylint returns a non-zero exit code when it finds issues
        # Capture the output and return it as part of the fail response
        return {
            "status": "fail",
            "message": e.output.strip()  # Return the raw pylint message as feedback
        }

    except FileNotFoundError:
        # If pylint is not installed or not found in the system's PATH
        return {
            "status": "fail",
            "message": "Pylint is not installed or not found in system path."
        }
    
# test
def run_pylint_code_smell2(filepath):
    return "2"