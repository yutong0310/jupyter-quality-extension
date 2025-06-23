# batch_analysis/metric_plots/cc_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns

from batch_analysis.extract_results import extract_metrics

# === Load Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)

# Exclude CC scores that are exactly 0 — these typically mean "no functions/classes"
cc_scores = [score for score in extracted_data["Cyclomatic Complexity"] if score > 0]

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot: Histogram with KDE and Count Labels ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 6))  # Increased height for better visibility

# Create histogram
ax = sns.histplot(cc_scores, bins=40, kde=True, color="cornflowerblue", edgecolor="black", linewidth=0.5)

# Add frequency labels on top of each bar
for patch in ax.patches:
    height = patch.get_height()
    if height > 0:
        ax.text(patch.get_x() + patch.get_width() / 2,
                height + 1,
                f"{int(height)}",
                ha='center', va='bottom', fontsize=9, fontweight="bold")

# Adjust y-limit to give room for labels
plt.ylim(top=max([p.get_height() for p in ax.patches]) + 20)

# Mean and median lines
mean_val = sum(cc_scores) / len(cc_scores)
median_val = sorted(cc_scores)[len(cc_scores) // 2]
plt.axvline(mean_val, color="red", linestyle="--", linewidth=1, label=f"Mean: {mean_val:.2f}")
plt.axvline(median_val, color="green", linestyle="--", linewidth=1, label=f"Median: {median_val:.2f}")

plt.title("Cyclomatic Complexity Score Distribution (Excluding 0s)")
plt.xlabel("Cyclomatic Complexity Score")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/cc_score_histogram.png", dpi=300)
plt.close()

print("✅ Cyclomatic Complexity histogram saved (0s excluded, with count labels).")