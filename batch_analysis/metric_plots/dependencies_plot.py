# batch_analysis/metric_plots/dependencies_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns

from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, status_summary = extract_metrics(json_path)

# Get dependency counts
dependency_data = extracted_data["Dependency Management"]  # List of 1 (pass) and 0 (fail)
pass_count = sum(dependency_data)
fail_count = len(dependency_data) - pass_count
total = len(dependency_data)

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot ===
sns.set(style="whitegrid", font_scale=1.3)
plt.figure(figsize=(8, 3.5))

bars = plt.barh(["Dependency Management"], [pass_count], color="mediumseagreen", label="pass", height=0.4)
bars2 = plt.barh(["Dependency Management"], [fail_count], left=[pass_count], color="salmon", label="fail", height=0.4)

# Labels
plt.text(pass_count / 2, 0, str(pass_count), ha="center", va="center", color="white", fontweight="bold")
plt.text(pass_count + fail_count / 2, 0, str(fail_count), ha="center", va="center", color="white", fontweight="bold")
plt.text(pass_count + fail_count + 5, 0, f"Total: {total}", va="center", color="gray")

# Style
plt.title("Dependency Management Pass vs Fail")
plt.xlabel("Number of Projects")
plt.xlim(0, pass_count + fail_count + 50)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(f"{output_dir}/dependencies_pass_fail_bar.png", dpi=300)
plt.close()

print("✅ Dependency management bar chart saved.")
