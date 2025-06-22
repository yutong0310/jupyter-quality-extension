import os # for directory handling
import re # for regular expression matching
import json # for saving results
import io # for capturing print output
from contextlib import redirect_stdout # to capture stdout from tool execution

from evaluation.evaluator import evaluate_metrics  # runs the tool logic
from lifecycle.stage_manager import get_metrics_for_stage  # maps stage to metrics

# --- Configuration ---
base_dir = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_test"  # Folder with downloaded repos
selected_stage = "Development"  # Fixed lifecycle stage to evaluate
# output_file = os.path.join(base_dir, "batch_cleaned_results.json")  # Where to store the cleaned result summary

# Get parent directory of base_dir
parent_dir = os.path.dirname(base_dir)

# Define results directory path
results_dir = os.path.join(parent_dir, "11_envri_validation_set_results")
os.makedirs(results_dir, exist_ok=True)  # Make sure the folder exists

# Define output file path inside the results directory
output_file = os.path.join(results_dir, "batch_development_results.json")

START_RESULTS_FLAG = "📁 Project-Level Results" # Indicator when results start
summary_results = {}  # Final dictionary to hold all project outputs

# Recognize Code Smell score lines like: "Your code has been rated at 4.55/10"
pylint_score_pattern = re.compile(r"rated at ([\d\.]+)/10")

def is_metric_start(line):
    """True if line is a new metric line (✓ or x)."""
    return line.strip().startswith(("✓", "x"))

def extract_code_smell_score(lines):
    """Find and return only the pylint score line from the text."""
    for line in lines:
        if "rated at" in line:
            return line.strip()
    return "N/A"

# --- Main loop ---
for project in os.listdir(base_dir):
    project_path = os.path.join(base_dir, project)
    if not os.path.isdir(project_path):
        continue

    print(f"Running analysis for: {project}")

    # Capture tool output for this project
    f = io.StringIO() # Create an in-memory text stream to capture printed output

    # Redirect standard output(stdout) to the StringIO object
    with redirect_stdout(f):
        try:
            metrics = get_metrics_for_stage(selected_stage)
            evaluate_metrics(metrics, path=project_path)
        except Exception as e:
            print(f"Error running tool on {project}: {e}")
            
            # DEBUG
            import traceback
            traceback.print_exc()
    
    # Get the captured output from the StringIO buffer
    raw_output = f.getvalue()
    if not raw_output.strip():
        print(f"⚠ No output captured for {project}")
        continue

    # DEBUG
    print(f"--- Output from {project} ---\n{raw_output[:1000]}\n--- END ---")

    # Split the output into individual lines
    lines = raw_output.splitlines()

    # --- Parse tool output ---
    results = {}
    scope = "📁 Project"  # default scope
    results[scope] = {}
    parsing = False

    # Go through each line (with its index) so we can also look ahead to the next line
    for i, line in enumerate(lines): 
        line = line.strip()

        # Start collecting results only after this flag
        if START_RESULTS_FLAG in line:
            parsing = True
            continue
        if not parsing:
            continue

        # Switch to file-level scope
        if line.startswith("📄 File:"):
            scope = line
            results[scope] = {}
            continue

        # Code smell block - extract pylint score
        if "Code Smells" in line:
            results[scope]["Code Smell Score"] = extract_code_smell_score(lines[i:])
            continue

        # Metric block: store ✓ or x + 2nd line (project-level) OR just ✓/x line (file-level)
        if is_metric_start(line):
            if scope == "📁 Project":
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                results[scope][line] = next_line
            else:
                results[scope][line] = "" # Only include the header line for file-level metrics

    summary_results[project] = results

# --- Save results ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(summary_results, f, indent=2)

print(f"\n ✓ All done! Results saved to: {output_file}")