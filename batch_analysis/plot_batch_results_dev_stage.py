import json
import os
import re
from collections import defaultdict
from batch_analysis.metric_plots import passfail_summary_plot


# === Path to results JSON ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"

# === Containers for Extracted Data ===
extracted_data = {
    "Maintainability Index": [],
    "Cyclomatic Complexity": [],
    "Cyclomatic Rank": [],
    "Comment Density": [],
    "Code Smells": [],
    "Software Size (LoC)": [],
    "Code Duplication": [],
    "Percentage of Assertions": [],
    "Dependencies": [],
}

# === Load JSON ===
with open(json_path, "r", encoding="utf-8") as f:
    all_results = json.load(f)

# === Metric Parsing Logic ===
for project, sections in all_results.items():
    for section_name, metrics in sections.items():

        # Project-level metrics
        if "Project-Level Results" in section_name:
            for metric_name, metric in metrics.items():
                if metric_name == "Software Size (LoC)":
                    extracted_data["Software Size (LoC)"].append(metric.get("loc", 0))
                elif metric_name == "Code Duplication":
                    extracted_data["Code Duplication"].append(metric.get("percentage", 0))
                elif metric_name == "Percentage of Assertions":
                    msg = metric.get("message", "")
                    match = re.search(r"Assertions found: (\d+)", msg)
                    count = int(match.group(1)) if match else 0
                    extracted_data["Percentage of Assertions"].append(count)
                elif metric_name == "Dependency Management":
                    status = metric.get("status", "").lower()
                    if status == "pass":
                        extracted_data["Dependencies"].append(1)
                    elif status == "fail":
                        extracted_data["Dependencies"].append(0)

        # Notebook-level metrics
        elif section_name.endswith(".py"):
            for metric_name, metric in metrics.items():
                if metric_name == "Maintainability Index":
                    extracted_data["Maintainability Index"].append(metric.get("score", 0))
                elif metric_name == "Cyclomatic Complexity":
                    extracted_data["Cyclomatic Complexity"].append(metric.get("score", 0))
                    rank = metric.get("rank", "")
                    if rank in {"A", "B", "C", "D", "E", "F"}:
                        extracted_data["Cyclomatic Rank"].append(rank)
                elif metric_name == "Comment Density":
                    extracted_data["Comment Density"].append(metric.get("density", 0))
                elif metric_name == "Code Smells":
                    msg = metric.get("message", "")
                    if "rated at" in msg:
                        try:
                            score = float(msg.split("rated at ")[1].split("/")[0])
                            extracted_data["Code Smells"].append(score)
                        except ValueError:
                            continue

# === Pass/Fail Summary for All 8 Metrics ===
status_summary = {
    "Maintainability Index": {"pass": 0, "fail": 0},
    "Cyclomatic Complexity": {"pass": 0, "fail": 0},
    "Comment Density": {"pass": 0, "fail": 0},
    "Code Smells": {"pass": 0, "fail": 0},
    "Software Size (LoC)": {"pass": 0, "fail": 0},
    "Code Duplication": {"pass": 0, "fail": 0},
    "Percentage of Assertions": {"pass": 0, "fail": 0},
    "Dependency Management": {"pass": 0, "fail": 0},
}

# Re-iterate to collect status info
for project, sections in all_results.items():
    for section_name, metrics in sections.items():

        if "Project-Level Results" in section_name:
            for metric_name, metric in metrics.items():
                if metric_name in status_summary:
                    status = metric.get("status", "").lower()
                    if status in ["pass", "fail"]:
                        status_summary[metric_name][status] += 1

        elif section_name.endswith(".py"):
            for metric_name, metric in metrics.items():
                if metric_name in status_summary:
                    status = metric.get("status", "").lower()
                    if status in ["pass", "fail"]:
                        status_summary[metric_name][status] += 1

# Optional: print summary
print("\n=== Pass/Fail Summary ===")
for metric, counts in status_summary.items():
    print(f"{metric}: ✅ {counts['pass']} pass, ❌ {counts['fail']} fail")

