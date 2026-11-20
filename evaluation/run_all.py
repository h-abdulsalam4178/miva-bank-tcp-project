import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    ("1. Score Runs", "score_runs.py"),
    ("2. Compute APFD", "compute_apfd.py"),
    ("3. Ranking Stability", "stability.py"),
    ("4. Weight Sensitivity", "weight_sensitivity.py"),
    ("5. Risk Model Comparison", "risk_model_comparison.py"),
]


def run_all():
    print("=" * 65)
    print("Running all evaluation scripts for Miva Bank prioritization")
    print("=" * 65)

    for label, script_name in SCRIPTS:
        script_path = os.path.join(HERE, script_name)
        print(f"\n--- {label} ({script_name}) ---")
        subprocess.run(
            [sys.executable, script_path],
            cwd=HERE,
            check=True,
        )

    print("\n" + "=" * 65)
    print("All evaluation scripts completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    run_all()
