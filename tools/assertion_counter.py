import os
import ast

def run_assertion_percentage(path):
    """
    Calculates the percentage of 'assert' statements in Python code.

    Args:
        path (str): File or folder path to scan.

    Returns:
        dict: Contains 'status' and 'message' with the result.
    """

    total_asserts = 0   # Number of assert statements
    total_statements = 0  # Total number of statements (executable)

    python_files = []

    # STEP 1: Collect all .py files
    if os.path.isfile(path) and path.endswith('.py'):
        python_files.append(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    else:
        return {
            "status": "fail",
            "message": f"Invalid path: {path}"
        }
    
    # STEP 2: Analyze each file
    for filepath in python_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()

            # Parse the file into an AST tree
            tree = ast.parse(source)

            # Count nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    total_asserts += 1
                if isinstance(node, ast.stmt):
                    total_statements += 1
        
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Error processing {filepath}: {str(e)}"
            }
    
    # STEP 3: Calculate result
    if total_statements == 0:
        return {
            "status": "pass",
            "message": "No executable code found to evaluate assertions."
        }
    
    percentage = (total_asserts / total_statements) * 100

    # STEP 4: Threshold: Pass if >= 5% assertions
    if percentage >= 5.0:
        status = "pass"
    else:
        status = "fail"
    
    return {
        "status": status,
        "message": f"Assertions found: {total_asserts} out of {total_statements} statements ({percentage:.2f}%)"
    }