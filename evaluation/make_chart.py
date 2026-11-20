import csv
import json
import os
import random
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX_PATH = os.path.join(HERE, "..", "demo_bank", "fault_matrix.csv")
RANKINGS_PATH = os.path.join(HERE, "rankings.json")
OUTPUT_CHART = os.path.join(HERE, "apfd_chart.png")


def load_matrix():
    with open(MATRIX_PATH, newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))
    return {row[0]: [int(x) for x in row[1:-1]] for row in rows[1:]}


def apfd(order, matrix):
    n = len(order)
    m = len(next(iter(matrix.values())))
    total = 0
    for bug in range(m):
        for position, test_id in enumerate(order, start=1):
            if matrix[test_id][bug] == 1:
                total += position
                break
    return 1 - total / (n * m) + 1 / (2 * n)


def generate_chart():
    matrix = load_matrix()
    original_order = list(matrix)

    # 1. Original order APFD
    orig_apfd = apfd(original_order, matrix)

    # 2. Random order APFD (mean of 100, seed 42)
    random.seed(42)
    random_scores = []
    for _ in range(100):
        shuffled = original_order[:]
        random.shuffle(shuffled)
        random_scores.append(apfd(shuffled, matrix))
    rnd_apfd = sum(random_scores) / len(random_scores)

    # 3. LLM-assisted APFD from official rankings
    with open(RANKINGS_PATH, encoding="utf-8") as file:
        rankings = json.load(file)
    llm_scores = [apfd(order, matrix) for order in rankings]
    llm_mean = sum(llm_scores) / len(llm_scores)
    llm_min = min(llm_scores)
    llm_max = max(llm_scores)

    # Plotting
    labels = ["Original Order", "Random Order\n(mean of 100)", "LLM-Assisted\n(5-run mean)"]
    values = [orig_apfd, rnd_apfd, llm_mean]
    colors = ["#7f7f7f", "#aec7e8", "#1f77b4"]

    # Asymmetric error bar for LLM run range [min, max]
    yerr = [
        [0, 0, llm_mean - llm_min],
        [0, 0, llm_max - llm_mean],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        labels,
        values,
        yerr=yerr,
        capsize=6,
        color=colors,
        edgecolor="#333333",
        linewidth=1,
        width=0.55,
        error_kw={"elinewidth": 1.5, "ecolor": "#d62728", "capthick": 1.5},
    )

    ax.set_ylabel("APFD Score (Higher is Better)", fontsize=11, fontweight="bold")
    ax.set_title("Test Prioritization APFD Comparison (Miva Bank)", fontsize=12, fontweight="bold", pad=14)
    ax.set_ylim(0.45, 0.62)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Annotate bar values
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f"{val:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Annotate range on LLM bar
    ax.annotate(
        f"range: [{llm_min:.3f}, {llm_max:.3f}]",
        xy=(bars[2].get_x() + bars[2].get_width() / 2, llm_max),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#d62728",
        fontweight="bold",
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_CHART, dpi=300)
    plt.close()
    print("Saved chart:", OUTPUT_CHART)


if __name__ == "__main__":
    generate_chart()
