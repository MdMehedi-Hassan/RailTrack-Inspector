import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Confusion matrix values (replace if needed)
cm = np.array([
    [190, 7,   0],
    [4,   192, 0],
    [0,   0,   200]
])

class_names = ["Bolt", "Fastener", "Railcrack"]
plt.figure(figsize=(14, 12))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Greens",
    xticklabels=class_names,
    yticklabels=class_names,
    annot_kws={"size": 20}   # numbers inside cells
)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlabel("True Label", fontsize=16)
plt.ylabel("Predicted Label", fontsize=16)
plt.title("Confusion Matrix", fontsize=18)

plt.tight_layout()

# Save high-quality image
plt.savefig(
    r"D:\Rail Paper_Thesis\Models\Latest\Faster R-CNN\confusion.png",
    dpi=300
)

plt.show()