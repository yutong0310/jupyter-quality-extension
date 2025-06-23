# batch_analysis/metric_plots/duplication_plot.py

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from batch_analysis.extract_results import extract_metrics

# === Load and Prepare Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)
duplication_values = extracted_data["Code Duplication"]

# === Sort values for CDF ===
sorted_vals = np.sort(duplication_values)
cdf_vals = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

# === Plot ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 6))
plt.plot(sorted_vals, cdf_vals, marker='.', linestyle='-', color='chocolate')

# Reference line: threshold
plt.axvline(15, linestyle="--", color="gray", alpha=0.5)
plt.text(15 + 1, 0.05, "15% Threshold", fontsize=10, color="gray")

# Mean/median
mean_val = np.mean(duplication_values)
median_val = np.median(duplication_values)
plt.axvline(mean_val, color="red", linestyle="--", label=f"Mean: {mean_val:.2f}%")
plt.axvline(median_val, color="green", linestyle="--", label=f"Median: {median_val:.2f}%")

# Axis & labels
plt.title("Cumulative Distribution of Code Duplication (%)")
plt.xlabel("Code Duplication (%)")
plt.ylabel("Cumulative Proportion of Projects")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()

# Save
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)
plt.savefig(f"{output_dir}/duplication_cdf_plot.png", dpi=300)
plt.close()

print("✅ Duplication CDF plot saved.")
