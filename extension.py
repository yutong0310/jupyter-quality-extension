"""
This module defines the user interface and lifecycle interaction for
the Jupyter extension that helps assess the quality of Tier-1 research software.
"""

import ipywidgets as widgets
from IPython.display import display, Markdown
from lifecycle.stage_manager import get_metrics_for_stage
from evaluation.evaluator import evaluate_metrics

# -------------------------------------------------------------------
# UI ELEMENTS: Create all the interactive components for the extension
# -------------------------------------------------------------------

# 1. Dropdown for selecting the current software development life cycle stage
stage_dropdown = widgets.Dropdown(
    options=["Planning and Design", "Development", "Testing", "Maintenance"],
    description="Stage:",  # Label next to the dropdown
    style={'description_width': 'initial'}  # Avoid clipping the label
)

# 2. Text input to let the user specify a Python file or folder to analyze
target_input = widgets.Text(
    value=".",  # Default value = current directory
    description="Target Path:",  # Label next to input box
    placeholder="e.g., script.py or src_folder/",  # Guide for the user
    style={'description_width': 'initial'}
)

# 3. Button that triggers the scan when clicked
run_button = widgets.Button(
    description="Run Quality Scan",  # Button label
    button_style='success'  # Green color
)

# 4. Output area for displaying results below the UI
output_area = widgets.Output()

# -------------------------------------------------------------------
# EVENT HANDLER: This function runs when the button is clicked
# -------------------------------------------------------------------

def on_run_button_click(_b):
    """
    This function is triggered when the 'Run Quality Scan' button is clicked.
    It:
    1. Reads selected stage and target path
    2. Gets applicable metrics for the selected stage
    3. Calls evaluator to run checks
    4. Displays results clearly using icons and Markdown formatting
    """
    output_area.clear_output()  # Clear previous results before new scan

    selected_stage = stage_dropdown.value          # Get user-selected life cycle stage
    target_path = target_input.value.strip()       # Get the path entered by the user

    with output_area:
        # Show selected stage and path
        display(Markdown(f"### Selected Stage: `{selected_stage}`"))
        display(Markdown(f" Target Path: `{target_path}`"))

        # STEP 1: Retrieve relevant metrics for the selected stage
        metrics = get_metrics_for_stage(selected_stage)
        display(Markdown(f"**Running {len(metrics)} checks...**"))

        # STEP 2: Run evaluation logic on selected file(s)
        results = evaluate_metrics(metrics, target_path)

        # STEP 3: Loop through each analyzed file and its results
        for file, file_metrics in results.items():
            # Display file name as a section header
            display(Markdown(f"---\n📄 **File: `{file}`**"))

            # For each metric applied to this file
            for metric, result in file_metrics.items():

                # Fallback: if the result is not a dictionary, just show the raw output
                if not isinstance(result, dict):
                    emoji = "❌"
                    message = str(result)
                else:
                    # Use green checkmark for "pass", red X for "fail"
                    emoji = "✅" if result.get("status") == "pass" else "❌"
                    # Show associated message (e.g., score, issues found)
                    message = result.get("message", "No message")

                # Display the result for this metric
                display(Markdown(f"- {emoji} **{metric}**: {message}"))

# -------------------------------------------------------------------
# CONNECT THE BUTTON TO ITS EVENT HANDLER
# -------------------------------------------------------------------

run_button.on_click(on_run_button_click)

# -------------------------------------------------------------------
# LAYOUT: Combine UI components into a vertical layout
# -------------------------------------------------------------------

ui = widgets.VBox([
    stage_dropdown,
    target_input,
    run_button,
    output_area
])

# -------------------------------------------------------------------
# DISPLAY THE FULL UI INSIDE THE JUPYTER NOTEBOOK
# -------------------------------------------------------------------

display(ui)