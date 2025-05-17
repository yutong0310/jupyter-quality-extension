import subprocess  
import os  

def run_pylint_code_smell(filepath):
    """
    Runs pylint on the specified Python file to detect code smells,
    and formats each issue line-by-line for better display.

    Args:
        filepath (str): The path to the Python file to analyze.

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'message': list of individual warnings or single summary
        }
    """
    if not os.path.isfile(filepath):
        return {
            "status": "fail",
            "message": [f"File not found: {filepath}"]
        }

    try:
        output = subprocess.check_output(
            ['pylint', filepath, '-f', 'text', '--disable=all', '--enable=C,R,W'],
            stderr=subprocess.STDOUT,
            text=True
        )

        lines = [line.strip() for line in output.strip().split('\n') if line.strip()]
        messages = [line for line in lines if ':' in line]

        return {
            "status": "fail" if messages else "pass",
            "message": messages if messages else ["No major code smells found."]
        }

    except subprocess.CalledProcessError as e:
        lines = [line.strip() for line in e.output.strip().split('\n') if line.strip()]
        messages = [line for line in lines if ':' in line]

        return {
            "status": "fail" if messages else "pass",
            "message": messages if messages else ["No major code smells found."]
        }
