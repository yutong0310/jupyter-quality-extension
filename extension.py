"""
This module defines the user interface and lifecycle interaction for
the Jupyter extension that helps assess the quality of Tier-1 research software.
"""

import ipywidgets as widgets
from IPython.display import display, HTML, Markdown
from lifecycle.stage_manager import get_metrics_for_stage
from evaluation.evaluator import evaluate_metrics
from evaluation.evaluator import display_maintenance_metric_overview

# -------------------------------------------------------------------
# UI ELEMENTS: Create all the interactive components for the extension
# -------------------------------------------------------------------

stage_dropdown = widgets.Dropdown(
    options=["Planning and Design", "Development", "Testing", "Maintenance"],
    description="Stage:",
    style={'description_width': 'initial'}
)

target_input = widgets.Text(
    value=".",
    description="Target Path:",
    placeholder="e.g., script.py or src_folder/",
    style={'description_width': 'initial'},
    layout=widgets.Layout(width="600px")  # Wider path input
)

github_url_input = widgets.Text(
    value="",
    description="GitHub URL:",
    placeholder="e.g., https://github.com/username/repo",
    style={'description_width': 'initial'},
    layout=widgets.Layout(visibility='hidden', width="600px", margin="0 0 10px 0")
)

run_button = widgets.Button(
    description="Run Quality Scan",
    button_style='success',
    layout=widgets.Layout(margin="0 0 15px 0")
)

output_area = widgets.Output()

# -------------------------------------------------------------------
# Button click event: handles all lifecycle logic
# -------------------------------------------------------------------

def on_run_button_click(_b):
    output_area.clear_output()

    selected_stage = stage_dropdown.value
    target_path = target_input.value.strip()
    github_url = github_url_input.value.strip()

    with output_area:
        display(Markdown(f"### Selected Stage: `{selected_stage}`"))

        metrics = get_metrics_for_stage(selected_stage)
        # display(Markdown(f"**Running {len(metrics)} quality checks...**"))

        if selected_stage == "Maintenance":
            display_maintenance_metric_overview()

        if selected_stage != "Maintenance":
            display(Markdown(f"Target Path: `{target_path}`"))

        # Perform evaluation
        results = evaluate_metrics(metrics, target_path, github_url)

        # STEP 1: Display project-level results if present
        if "Project-Level Results" in results:
            project_metrics = results["Project-Level Results"]
            display(Markdown("---"))
            display(Markdown("📁 **Project-Level Results**"))

            # Explain what metrics Howfairis contributes to
            if "FAIR Assessment (howfairis)" in project_metrics:
                display(HTML("<i>Howfairis contributes to the following metrics: "
                            "<b>Presence of License</b>, "
                            "<b>Publicly Accessible Repository</b>, "
                            "<b>Rich Metadata</b> (partially), and "
                            "<b>Documentation Quality</b> (partially).</i><br><br>"))

            for metric, result in project_metrics.items():
                if metric.startswith("-----divider"):
                    display(Markdown("---"))
                    continue

                display(Markdown(f"**{metric}**"))

                if isinstance(result, dict):
                    raw_output = result.get("message", "").strip()
                    for line in raw_output.splitlines():
                        if line.strip():  # skip empty lines
                            display(Markdown(line.strip()))
                else:
                    display(Markdown(str(result)))
            
            # display(Markdown("**User Satisfaction (Manual Assessment)**"))
            # display(HTML("⚠️ <b>User Satisfaction</b>: Not automatically measurable. This requires user surveys or interviews."))

        # STEP 2: Display file-level results (skip if Maintenance stage)
        if selected_stage != "Maintenance":
            for file, file_metrics in results.items():
                if file == "Project-Level Results":
                    continue

                display(Markdown(f"---\n📄 **File: `{file}`**"))
                for metric, result in file_metrics.items():
                    if isinstance(result, dict):
                        status = result.get("status", "")
                        message = result.get("message", "")
                        icon = "✅" if status == "pass" else "❌"
                        display(Markdown(f"- {icon} **{metric}**: {message}"))
                    else:
                        display(Markdown(f"- **{metric}**: {result}"))

# -------------------------------------------------------------------
# Toggle visibility for GitHub input
# -------------------------------------------------------------------

def on_stage_change(change):
    if change['new'] == "Maintenance":
        github_url_input.layout.visibility = 'visible'
        target_input.layout.visibility = 'hidden'
    else:
        github_url_input.layout.visibility = 'hidden'
        target_input.layout.visibility = 'visible'

stage_dropdown.observe(on_stage_change, names='value')

# -------------------------------------------------------------------
# Render the UI
# -------------------------------------------------------------------

run_button.on_click(on_run_button_click)

ui = widgets.VBox([
    stage_dropdown,
    target_input,
    github_url_input,
    run_button,
    output_area
])

display(ui)
