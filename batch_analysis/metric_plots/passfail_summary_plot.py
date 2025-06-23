# batch_analysis/metric_plots/passfail_summary_plot.py

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

from batch_analysis.extract_results import extract_metrics

json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
_, status_summary = extract_metrics(json_path)

output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Prepare Data ===
df = pd.DataFrame(status_summary).T
df = df[["pass", "fail"]]  # Keep only necessary columns
df["total"] = df["pass"] + df["fail"]  # Create 'total' before modifying

# === Metrics needing zero exclusion ===
metrics_to_adjust = ["Code Smells", "Cyclomatic Complexity"]

for metric in metrics_to_adjust:
    if metric in df.index:
        zero_count = status_summary[metric].get("zero", 0)  # Assume 'zero' count is stored here
        df.at[metric, "fail"] = max(df.at[metric, "fail"] - zero_count, 0)
        df.at[metric, "total"] = df.at[metric, "pass"] + df.at[metric, "fail"]


# Keep only necessary columns
df = df[["pass", "fail"]]
df["total"] = df["pass"] + df["fail"]
df = df.sort_values(by="fail", ascending=True)

# === Color Scheme (ColorBrewer: Set2) ===
pass_color = "#8dd3c7"
fail_color = "#fb8072"

# === Plot ===
plt.figure(figsize=(12, 7))
sns.set(style="whitegrid", font_scale=1.1)
bars = df[["pass", "fail"]].plot(
    kind="barh",
    stacked=True,
    figsize=(12, 7),
    color=[pass_color, fail_color],
    edgecolor="black"
)

plt.title("Pass vs Fail Projects for Each Metric", fontsize=16)
plt.xlabel("Number of Projects / Files Evaluated")
plt.ylabel("Quality Metric")
plt.legend(title="Status")
plt.grid(axis="x", linestyle="--", alpha=0.5)

# === Add Smart Labels ===
for i, (metric, row) in enumerate(df.iterrows()):
    pass_val = row["pass"]
    fail_val = row["fail"]
    total = row["total"]

    def label_color(val): return "white" if val > 30 else "black"

    pass_x = pass_val / 2 if pass_val > 30 else pass_val + 6
    fail_x = pass_val + fail_val / 2 if fail_val > 30 else pass_val + fail_val - 6

    pass_ha = "center" if pass_val > 30 else "left"
    fail_ha = "center" if fail_val > 30 else "right"

    plt.text(pass_x, i, f"{pass_val}", ha=pass_ha, va="center",
             color=label_color(pass_val), fontsize=9, fontweight="bold")

    plt.text(fail_x, i, f"{fail_val}", ha=fail_ha, va="center",
             color=label_color(fail_val), fontsize=9, fontweight="bold")

    plt.text(pass_val + fail_val + 10, i, f"  Total: {total}",
             color="gray", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(f"{output_dir}/metric_pass_fail_bar.png", dpi=300)
plt.close()

print("✅ Chart updated with smarter labels and improved colors (0s excluded for specific metrics).")