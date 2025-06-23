# batch_analysis/metric_plots/loc_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)
loc_values = extracted_data["Software Size (LoC)"]

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Filter: Exclude 0 or invalid LoC values ===
loc_array = np.array([val for val in loc_values if val > 0])
total_projects = len(loc_array)

# === Set Style ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 6))

# === Plot Histogram with Log-scaled x-axis ===
# Log scale helps visualize both small and large projects clearly
ax = sns.histplot(loc_array, bins=40, kde=True, color="mediumseagreen", edgecolor="black", linewidth=0.5, log_scale=(True, False))

# Add count labels above bars with slight vertical spacing
for patch in ax.patches:
    height = patch.get_height()
    if height > 0:
        ax.text(patch.get_x() + patch.get_width() / 2,
                height + 0.5,  # Increased offset
                f"{int(height)}",
                ha='center', va='bottom', fontsize=9, fontweight="bold")

# Mean and median reference lines
mean_val = loc_array.mean()
median_val = np.median(loc_array)
plt.axvline(mean_val, color="red", linestyle="--", linewidth=1, label=f"Mean: {int(mean_val)}")
plt.axvline(median_val, color="green", linestyle="--", linewidth=1, label=f"Median: {int(median_val)}")

# === Add annotation for total number of projects ===
plt.text(0.98, 0.95, f"Total Projects: {total_projects}",
         transform=plt.gca().transAxes,
         ha="right", va="top",
         fontsize=11, color="gray")

# === Final touches ===
plt.xlabel("Lines of Code (LoC, log scale)")
plt.ylabel("Frequency")
plt.title("Distribution of Lines of Code (Log-scaled)")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/loc_distribution_log_hist.png", dpi=300)
plt.close()

print("✅ LoC distribution plot saved with annotation and spacing improvements.")
