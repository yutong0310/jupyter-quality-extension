# batch_analysis/metric_plots/assertions_plot.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)
assertion_counts = extracted_data["Percentage of Assertions"]

# === Output directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot Settings ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 2.8))

# === Strip plot with enhanced jitter & size ===
sns.stripplot(
    x=assertion_counts,
    size=4,               # Smaller dots to reduce stacking
    jitter=0.35,          # More jitter for better spread
    color="#008b8b",      # Deep teal for visibility
    alpha=0.8
)

# === Highlight 0-assertion group with annotation ===
zero_count = assertion_counts.count(0)
plt.annotate(
    f"{zero_count} projects with 0 assertions",
    xy=(0, 0.15),
    xytext=(10, 0.3),
    arrowprops=dict(arrowstyle="->", color="gray", linewidth=1),
    fontsize=11,
    color="black",
    fontweight="bold"
)

# === Final Styling ===
plt.title("Assertion Count per Project (Prominent 0 Cluster)")
plt.xlabel("Number of Assertions")
plt.yticks([])  # Hide y-axis
plt.xlim(-1, 100)
plt.tight_layout()
plt.savefig(f"{output_dir}/assertions_stripplot.png", dpi=300)
plt.close()

print("✅ Assertion stripplot saved.")
