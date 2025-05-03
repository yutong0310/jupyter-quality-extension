import os
import subprocess
import json

def run_jscpd_code_duplication(path):
    """
    Runs jscpd on the given path (file or folder) to detect code duplication.
    Parses the JSON report and returns duplication percentage. 

    Args:
        path (str): Path to a Python file or folder. 

    Returns:
        dict: {
            'status': 'pass' or 'fail',
            'percentage': float,
            'message': str
        }
    """

    # Step 1: Validate path exists
    if not os.path.exists(path):
        return {
            "status": "fail",
            "message": f"Path does not exist: {path}"
        }
    
    # Step 2: Set output directory for the jscpd report
    # It defines where jscpd will save the JSON output report (which contains the code duplication results).
    # This builds the full path to the report file: ./jscpd-report/jscpd-report.json
    # This is where code later looks to read back the analysis results. 
    output_dir = "./jscpd-report"
    report_file = os.path.join(output_dir, "jscpd-report.json")

    try:
        # Step 3: Run jscpd using subprocess
        subprocess.run(
            [
                "jscpd",
                "--min-lines", "5",              # Minimum lines to consider duplication
                "--reporters", "json",           # Output format
                "--output", output_dir,          # Output directory
                path                             # File or folder to scan
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Step 4: Ensure report file was generated
        if not os.path.isfile(report_file):
            return {
                "status": "fail",
                "message": "jscpd report not found. Analysis may have failed."
            }
        
        # Step 5: Load JSON results
        with open(report_file, "r", encoding="utf-8") as f:
            # Parse the JSON content from the file and load it into a Python dictionary
            data = json.load(f)

        # Step 6: Extract total and duplicated line counts
        stats = data.get("statistics", {}).get("total", {})
        duplicated = stats.get("duplicatedLines", 0)
        total = stats.get("lines", 0)

        # Step 7: Calculate percentage duplicated
        percentage = (duplicated / total * 100) if total > 0 else 0

        # Step 8: Apply threshold logic (pass if < 15%)
        status = "pass" if percentage < 15 else "fail"

        return {
            "status": status,
            "percentage": percentage,
            "message": f"Code Duplication: {percentage:.2f}% duplicated code detected." if status == "pass"
                       else f"High Duplication: {percentage:.2f}% (❌ consider refactoring)"
        }
    
    except subprocess.CalledProcessError as e:
        return {
            "status": "fail",
            "message": f"jscpd error: {e.stderr.strip()}"
        }
    
    except Exception as e:
        return {
            "status": "fail",
            "message": f"Unexpected error while running jscpd: {str(e)}"
        }
