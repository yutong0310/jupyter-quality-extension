# batch_analysis/metric_plots/comments_plot.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from batch_analysis.extract_results import extract_metrics

# === Load & Clean Data ===
json_path = "/Users/yt/Documents/folder2024/course/Thesis/11_envri_validation_set_results/batch_development_results.json"
extracted_data, _ = extract_metrics(json_path)
densities = [d for d in extracted_data["Comment Density"] if d >= 0]

# === Bin comment densities ===
bins = [0, 1, 10, 20, 30, 40, 50, 60, 100]
labels = ["0%", "1–10%", "11–20%", "21–30%", "31–40%", "41–50%", "51–60%", ">60%"]
binned = pd.cut(densities, bins=[-0.01, 0.01, 10, 20, 30, 40, 50, 60, 100], labels=labels, right=True)
bin_counts = binned.value_counts().sort_index()

# === Output Directory ===
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# === Plot ===
sns.set(style="whitegrid", font_scale=1.2)
plt.figure(figsize=(10, 6))
ax = sns.barplot(x=bin_counts.values, y=bin_counts.index, palette="summer")

# Add bar labels
for i, val in enumerate(bin_counts.values):
    ax.text(val + 5, i, str(val), color="black", va="center", fontsize=10, fontweight="bold")

plt.title("Distribution of Comment Density Across Projects")
plt.xlabel("Number of Notebooks")
plt.ylabel("Comment Density Range")
plt.tight_layout()
plt.savefig(f"{output_dir}/comment_density_binned_bar.png", dpi=300)
plt.close()

print("✅ Horizontal bar chart for comment density saved.")
