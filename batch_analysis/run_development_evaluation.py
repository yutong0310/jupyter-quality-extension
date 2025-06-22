import os
import json
import subprocess
from bs4 import BeautifulSoup # For stripping HTML
from pathlib import Path 

# --- Configuration ---
base_dir = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_test"  
selected_stage = "Development"  

parent_dir = os.path.dirname(base_dir) # Get parent directory of base_dir
results_dir = os.path.join(parent_dir, "11_envri_validation_set_results") # Define results directory path
os.makedirs(results_dir, exist_ok=True)  # Make sure the folder exists
output_file = os.path.join(results_dir, "batch_development_results.json") # Define output file path inside the results directory

summary_results = {}  # Final dictionary to hold all project outputs

# Go through all projects in base_dir
for project in os.listdir(base_dir):
    project_path = os.path.join(base_dir, project)
    if not os.path.isdir(project_path):
        continue

    print(f"Running analysis for: {project}")

    # Run the CLI tool and capture its stdout
    try:
        result = subprocess.run(
            [
                "python",
                "run_quality_scan_cli.py",
                "--stage", selected_stage,
                "--path", project_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running CLI for {project}: {e}")
        continue

    stdout = result.stdout.strip()
    if not stdout:
        print(f"⚠ No output for {project}")
        continue

    # Find the json block from the CLI output
    json_start = stdout.find("{")
    if json_start == -1:
        print(f"⚠ Failed to locate JSON result in CLI output for {project}")
        continue

    try:
        parsed_results = json.loads(stdout[json_start:])
    except json.JSONDecodeError as e:
        print(f"⚠ JSON decode error for {project}: {e}")
        continue

    # Clean up the parsed_results in-place 
    for section_name, section_metrics in parsed_results.items():
        for metric_name, metric_result in section_metrics.items():
            if isinstance(metric_result, dict) and "message" in metric_result:
                message = metric_result["message"]

                # Case 1: Code Smells - keep only pylint score line 
                if metric_name == "Code Smells":
                    lines = message.splitlines()
                    score_line = next(
                        (line.strip() for line in lines if line.strip().startswith("Your code has been rated at")),
                        None 
                    )
                    if score_line:
                        metric_result["message"] = score_line
                    else:
                        metric_result["message"] = "N/A"
                    continue

                # Case 2: Other messages - clean HTML and keep top 1-2 lines only
                clean_text = BeautifulSoup(message, "html.parser").get_text(separator="\n")
                lines = [line.strip() for line in clean_text.splitlines() if line.strip()]

                # Filter out lines that start with 'Tip:' or 'Note:'
                main_lines = [line for line in lines if not line.lower().startswith(("tip:", "note:"))]

                # Keep only the first 1-2 relevant lines
                trimmed = main_lines[:2] if main_lines else ["N/A"]
                metric_result["message"] = " ".join(trimmed)

    # Store cleaned result into summary
    summary_results[project] = parsed_results

# --- Save final results ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summary_results, f, indent=2)

print(f"\n ✓ All done! Results saved to: {output_file}")