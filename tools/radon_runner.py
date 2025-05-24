import subprocess  # Used to run external system commands (like calling radon)
import json        # Used to parse the JSON output returned by radon
import os          # Used to check if the target file exists

def run_radon_maintainability_index(filepath):
    """
    Uses the 'radon' tool to compute the Maintainability Index (MI)
    for a given Python file. The MI score helps estimate how maintainable
    a codebase is, based on complexity, length, and other factors.

    Args:
        filepath (str): Path to the Python (.py) file to analyze.

    Returns:
        dict: A result dictionary containing:
            - 'status': "pass" or "fail"
            - 'score': the numeric MI score (float)
            - 'grade': letter grade assigned by radon (e.g., A, B, C)
            - 'message': formatted summary for display

        - The score is considered a "fail" if it's below 65 (standard threshold).
        - The function also handles errors and missing file cases.
    """

    # Step 1: Check whether the file exists
    if not os.path.isfile(filepath):
        return {
            "status": "fail",
            "message": f"File not found: {filepath}"  
        }

    try:
        # Step 2: Run radon to compute Maintainability Index
        # '--json' makes sure we get structured output that we can parse
        output = subprocess.check_output(
            ['radon', 'mi', '--json', filepath],  # CLI command: radon mi --json target.py
            stderr=subprocess.STDOUT,             # Capture any errors in output too
            text=True                             # Return output as a string, not bytes
        )

        # Step 3: Convert radon's JSON output into a Python dictionary
        results = json.loads(output)

        # Step 4: Extract the result for the specific file being analyzed
        file_result = results.get(filepath, {})  # Safely get result block or empty dict
        mi_score = file_result.get("mi")         # Numeric MI score
        mi_rank = file_result.get("rank")        # Letter grade (A, B, C, etc.)

        # Step 5: If both values are present, proceed to evaluate them
        if mi_score is not None and mi_rank is not None:

            grade_explanations = {
                "A": {
                    "note": "Very high maintainability.",
                    "tip": (
                        "Your code demonstrates excellent structure, clarity, and low complexity. "
                        "To maintain this level, continue enforcing consistent naming conventions, "
                        "modular design principles, and clean separation of concerns. "
                        "Ensure all functions remain concise and well-documented. "
                        "Conduct occasional code reviews to catch early signs of complexity."
                    )
                },
                "B": {
                    "note": "Moderate maintainability.",
                    "tip": (
                        "Your code is functional but may contain areas of growing complexity. "
                        "Focus on refactoring larger functions into smaller, reusable ones. "
                        "Add or improve comments and docstrings to enhance clarity for future maintainers. "
                        "Look out for inconsistent naming or coupled modules that could be abstracted. "
                        "Regular cleanup and consistent formatting will help elevate maintainability."
                    )
                },
                "C": {
                    "note": "Extremely low maintainability.",
                    "tip": (
                        "The codebase likely suffers from long, complex functions, poor documentation, "
                        "and high coupling between modules. Start by identifying the most complex areas "
                        "using tools like cyclomatic complexity. Break large functions into simpler, single-responsibility units. "
                        "Remove or consolidate redundant code, and use clear, descriptive naming. "
                        "Comprehensive docstrings and consistent structure will drastically improve maintainability."
                    )
                }
            }

            mi_note = grade_explanations.get(mi_rank, {}).get("note", "")
            mi_tip = grade_explanations.get(mi_rank, {}).get("tip", "")
            
            styled_note = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><i>{mi_note}</i></div>"
            styled_tip = f"<div style='margin-left: 20px; color: gray; font-size: 90%;'><b>Tip:</b> {mi_tip}</div>"

            full_message = (
                f"MI Score: {mi_score:.2f}, Grade: {mi_rank}"
                f"{styled_note}{styled_tip}"
            )

            # Step 6: Apply quality threshold (commonly used is 65)
            return {
                "status": "pass" if mi_score >= 65 else "fail",
                "score": mi_score,
                "grade": mi_rank,
                "message": full_message
            }

        # Step 7: Handle the case where MI score or grade is missing
        else:
            return {
                "status": "fail",
                "message": "Unable to parse MI score from radon output."
            }

    except subprocess.CalledProcessError as e:
        # If radon crashes or returns a non-zero exit code, capture the error
        return {
            "status": "fail",
            "message": f"Radon error: {e.output.strip()}"
        }

def run_radon_cyclomatic_complexity(filepath):
    """
    Computes the average Cyclomatic Complexity for a given Python file
    using Radon's command-line interface.

    Cyclomatic Complexity is a code metric that counts the number of independent
    paths through the code (e.g., due to loops, conditionals, etc.).
    Lower complexity means easier-to-understand and testable code.

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'score': float (average complexity),
            'message': str (summary for display)
        }
    """

    # Step 1: Make sure the file exists
    if not os.path.isfile(filepath):
        return {
            "status": "fail",
            "message": f"File not found: {filepath}" 
        }
    
    try:
        # Step 2: Run the radon complexity (cc) command in JSON mode
        output = subprocess.check_output(
            ['radon', 'cc', '--json', '--no-assert', filepath], # radon cc = complexity check
            stderr=subprocess.STDOUT, # Redirect any error output into the same stream
            text=True # Ensure the result is returned as a string (not bytes)
        )

        # Step 3: Parse the JSON output into a Python dictionary
        results = json.loads(output)

        # Step 4: Get the result list for the specific file
        # This will contain one dictionary per function/method

        # For example:
        # {"pylint_runner.py": 
        #   [{"type": "function", "rank": "A", "lineno": 4, "col_offset": 0, "name": "run_pylint_code_smell", "endline": 51, "complexity": 4, "closures": []}, 
        #    {"type": "function", "rank": "A", "lineno": 54, "col_offset": 0, "name": "run_pylint_code_smell2", "endline": 55, "complexity": 1, "closures": []}]
        # }
        file_results = results.get(filepath, [])

        # Step 5: Extract the cyclomatic complexity score for each function
        scores = [ item.get("complexity", 0) for item in file_results ]

        # Step 6: If there are no functions/methods found, return a default passing result
        if not scores:
            return {
                "status": "pass",
                "score": 0,
                "message": "No functions or classes found for cyclomatic complexity analysis."
            }
        
        # Step 7: Calculate the average complexity score
        average = sum(scores) / len(scores)

        # Step 8: Determine whether it passes based on a threshold (10 is common)
        status = "pass" if average < 10 else "fail"

        # Step 9: Return a summary of the result
        return {
            "status": status,
            "score": average,
            "message": f"Avg. Cyclomatic Complexity: {average:.2f}" if status == "pass"
                       else f"High Cyclomatic Complexity: {average:.2f} (❌ consider reducing complexity)"
        }
    
    except subprocess.CalledProcessError as e:
        # Step 10: If radon crashes (e.g., due to syntax error), catch and return error message
        return {
            "status": "fail",
            "message": f"Radon error: {e.output.strip()}"
        }
    
def run_radon_comment_density(filepath):
    """
    Calculates the comment density of a Python file using Radon's raw analysis.

    Comment Density = (comment_lines / source_lines) * 100
    where:
        - comment_lines = single-line comments + multi-line comment blocks
        - source_lines = SLOC (source lines of code)

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'density': float (percentage),
            'message': str
        }
    """

    # Step 1: Check if the target file exists
    if not os.path.isfile(filepath):
        return {
            "status": "fail",
            "message": f"File not found: {filepath}"
        }
    
    try:
        # Step 2: Run radon raw analysis with --json output
        output = subprocess.check_output(
            ['radon', 'raw', '--json', filepath],
            stderr=subprocess.STDOUT,
            text=True
        )

        # Step 3: Parse the output JSON into a Python dictionary
        results = json.loads(output)

        # Step 4: Extract the values for the specified file
        stats = results.get(filepath, {})
        sloc = stats.get("sloc", 0) # Source lines of code (non-empty, non-comment)
        comments = stats.get("comments", 0) # Single-line comments (#)
        multi = stats.get("multi", 0) # Multi-line docstrings or block comments

        # Step 5: Calculate the total number of comment lines
        comment_lines = comments + multi

        # Step 6: Compute the comment density percentage
        density = (comment_lines / sloc * 100) if sloc > 0 else 0

        # Step 7: Define pass/fail threshold (e.g., pass if density >= 10%)
        status = "pass" if density >= 10 else "fail"

        # Step 8: Return a standardized result dictionary
        return {
            "status": status,
            "density": density,
            "message": f"Comment Density: {density:.2f}%"
        }
    
    except subprocess.CalledProcessError as e:
        # If radon fails due to a code issue or bad syntax
        return {
            "status": "fail",
            "message": f"Radon error: {e.output.strip()}"
        }
    
    except Exception as e:
        # Catch any other unexpected errors
        return {
            "status": "fail",
            "message": f"Error calculating comment density: {str(e)}"
        }