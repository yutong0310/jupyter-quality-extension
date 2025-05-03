import os
import ast

def run_unit_test_detection(path):
    """
    Analyzes Python files in a given path to detect basic unit testing behavior.
    Counts number of 'assert' statements and 'test_*' functions.

    Args:
        path (str): Path to a Python file or directory.

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'assert_count': int,
            'test_function_count': int,
            'message': str
        }
    """
    total_asserts = 0
    test_functions = 0
    python_files = []

    if os.path.isfile(path) and path.endswith(".py"):
        python_files.append(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
    else:
        return {
            "status": "fail",
            "message": f"Invalid path: {path}"
        }
    
    for filepath in python_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()

            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    total_asserts += 1
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_functions += 1
        
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Error processing {filepath}: {str(e)}"
            }
        
    # Simple threshold logic: "pass" if any testing behavior found
    if total_asserts > 0 or test_functions > 0:
        status = "pass"
    else:
        status = "fail"

    return {
        "status": status,
        "assert_count": total_asserts,
        "test_function_count": test_functions,
        "message": f"Detected {total_asserts} assert statements and {test_functions} test-like functions."
    }
