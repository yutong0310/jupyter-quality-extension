# batch_analysis/metric_plots/code_smells_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns

from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)

# Exclude scores that are 0 — likely caused by notebook conversion issues
code_smell_scores = [score for score in extracted_data["Code Smells"] if score > 0]

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot: Histogram with KDE and Count Labels ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 6))

# Histogram + KDE
ax = sns.histplot(code_smell_scores, bins=30, kde=True, color="mediumpurple", edgecolor="black", linewidth=0.5)

# Add count labels
for patch in ax.patches:
    height = patch.get_height()
    if height > 0:
        ax.text(patch.get_x() + patch.get_width() / 2,
                height + 0.5,
                f"{int(height)}",
                ha='center', va='bottom', fontsize=9, fontweight="bold")

# Mean/Median lines
mean_val = sum(code_smell_scores) / len(code_smell_scores)
median_val = sorted(code_smell_scores)[len(code_smell_scores) // 2]
plt.axvline(mean_val, color="red", linestyle="--", linewidth=1, label=f"Mean: {mean_val:.2f}")
plt.axvline(median_val, color="green", linestyle="--", linewidth=1, label=f"Median: {median_val:.2f}")

plt.title("Code Smell Score Distribution (Pylint Ratings, 0s Excluded)")
plt.xlabel("Pylint Score")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/code_smells_score_histogram.png", dpi=300)
plt.close()

print("✅ Code Smell score histogram saved (0s excluded).")