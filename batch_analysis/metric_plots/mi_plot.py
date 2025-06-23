# batch_analysis/metric_plots/mi_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)
mi_scores = extracted_data["Maintainability Index"]

# === Filter valid scores ===
mi_scores = [score for score in mi_scores if isinstance(score, (int, float)) and 0 <= score <= 100]
total_projects = len(mi_scores)

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot: Strip Plot Only ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(12, 5))

# Strip plot (jittered for visibility)
sns.stripplot(x=mi_scores, color="dimgray", size=3, jitter=0.3, alpha=0.6)

# Mean and median lines
mean_val = np.mean(mi_scores)
median_val = np.median(mi_scores)
plt.axvline(mean_val, color="red", linestyle="--", linewidth=1, label=f"Mean: {mean_val:.2f}")
plt.axvline(median_val, color="green", linestyle="--", linewidth=1, label=f"Median: {median_val:.2f}")

# Annotation for total projects
plt.text(0.99, 0.95, f"Total Projects: {total_projects}", transform=plt.gca().transAxes,
         ha="right", va="top", fontsize=11, color="gray")

# Final Touches
plt.xlabel("Maintainability Index Score (0–100)")
plt.yticks([])
plt.title("Maintainability Index Score Distribution")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/mi_score_stripplot.png", dpi=300)
plt.close()

print("✅ Maintainability Index strip plot saved.")
