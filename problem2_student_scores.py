"""
Problem Statement 1.2 — Data Processing and Visualization
==========================================================
Fetch student test-score data from a public API, calculate the average
score per student, and create a bar chart to visualize the results.

Assumption:
    The JSONPlaceholder "todos" endpoint (https://jsonplaceholder.typicode.com/todos)
    is used as a stand-in for the "student scores API" because it is a free,
    reliable, public REST API that returns structured JSON.

    Mapping applied:
        • Each unique `userId`  → a student   (Student 1 … Student 10)
        • Each todo's `id`      → a test item
        • Score is derived as:  completed == True  → 100,  False → 40
          (simulates pass/fail grading on a 0–100 scale)

    This gives a realistic dataset of 10 students with ~20 scores each,
    which is ideal for demonstrating averaging and bar-chart visualisation.

Dependencies:
    pip install requests matplotlib
"""

import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL = "https://jsonplaceholder.typicode.com/todos"


# ---------------------------------------------------------------------------
# Step 1: Fetch data from the API
# ---------------------------------------------------------------------------
def fetch_scores(api_url: str) -> list[dict]:
    """
    Retrieve todo items and convert them into a list of
    {student_id, student_name, score} records.
    """
    print("Fetching student score data from API …")
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"[ERROR] API request failed: {exc}")
        return []

    todos = response.json()
    scores = [
        {
            "student_id":   item["userId"],
            "student_name": f"Student {item['userId']:02d}",
            "score":        100 if item["completed"] else 40,
        }
        for item in todos
    ]
    print(f"  → {len(scores)} score records retrieved across "
          f"{len({s['student_id'] for s in scores})} students.")
    return scores


# ---------------------------------------------------------------------------
# Step 2: Calculate average score per student
# ---------------------------------------------------------------------------
def calculate_averages(scores: list[dict]) -> dict[str, float]:
    """
    Return an ordered dict mapping student_name → average score,
    sorted by student_id (ascending).
    """
    totals: dict[str, list] = {}
    for record in scores:
        name  = record["student_name"]
        score = record["score"]
        if name not in totals:
            totals[name] = []
        totals[name].append(score)

    averages = {name: sum(vals) / len(vals) for name, vals in totals.items()}

    # Sort by student number
    averages = dict(sorted(averages.items(), key=lambda kv: int(kv[0].split()[1])))

    print("\nAverage scores per student:")
    print(f"  {'Student':<14} {'Avg Score':>9}  {'Tests Taken':>11}")
    print("  " + "-" * 38)
    for name, avg in averages.items():
        count = len(totals[name])
        print(f"  {name:<14} {avg:>9.1f}  {count:>11}")

    overall = sum(averages.values()) / len(averages)
    print(f"\n  Overall class average: {overall:.1f}")
    return averages


# ---------------------------------------------------------------------------
# Step 3: Visualize with a bar chart
# ---------------------------------------------------------------------------
def plot_bar_chart(averages: dict[str, float], output_path: str = "student_scores.png") -> None:
    """
    Render a colour-coded horizontal bar chart of average scores,
    annotate each bar, draw a class-average reference line, and save to PNG.
    """
    names  = list(averages.keys())
    values = list(averages.values())
    class_avg = sum(values) / len(values)

    # Colour bars: green if above average, coral if below
    colors = ["#4CAF50" if v >= class_avg else "#FF6B6B" for v in values]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(names, values, color=colors, edgecolor="white", height=0.6)

    # Annotate score values at the end of each bar
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}",
            va="center", ha="left",
            fontsize=9, color="#333333",
        )

    # Class-average reference line
    ax.axvline(class_avg, color="#1565C0", linewidth=1.6, linestyle="--",
               label=f"Class avg: {class_avg:.1f}")

    # Formatting
    ax.set_xlabel("Average Score (out of 100)", fontsize=11)
    ax.set_title("Student Average Test Scores", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlim(0, 115)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.invert_yaxis()   # highest student ID at the bottom
    ax.legend(loc="lower right", fontsize=10)

    # Legend patch for colour meaning
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#4CAF50", label="Above class average"),
        Patch(facecolor="#FF6B6B", label="Below class average"),
    ]
    ax.legend(handles=legend_elements + [
        plt.Line2D([0], [0], color="#1565C0", linewidth=1.6,
                   linestyle="--", label=f"Class avg: {class_avg:.1f}")
    ], loc="lower right", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"\nBar chart saved to '{output_path}'.")
    plt.show()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    scores   = fetch_scores(API_URL)
    if not scores:
        return
    averages = calculate_averages(scores)
    plot_bar_chart(averages)


if __name__ == "__main__":
    main()
