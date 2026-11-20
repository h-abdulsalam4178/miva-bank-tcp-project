# Evaluation Scripts and Reproduction Guide

This directory contains the experimental evaluation and benchmark replication scripts for the thesis project: *Intelligent Risk-Based Test Case Prioritization System Using Large Language Models for Financial Web Applications*.

All scripts use the official 5 LLM benchmark runs (Gemini 3.5 Flash Lite, prompt v1.0) isolated by `config.py` from `prototype/run_logs/runs.jsonl`.

---

## 1. Single-Command Reproduction

To run the entire evaluation pipeline and reproduce every benchmark result in sequence, run:

```bash
python evaluation/run_all.py
```

---

## 2. Individual Reproduction Commands (In Order)

If you prefer to run each analysis step individually, execute them in this order:

1. **Score Official Runs & Generate Rankings**
   ```bash
   python evaluation/score_runs.py
   ```
   *Scores each test case across the 5 official runs using the default weighted risk formula and writes the ordered rankings to `rankings.json`.*

2. **Compute APFD Metric & Detection Rates**
   ```bash
   python evaluation/compute_apfd.py
   ```
   *Calculates the Average Percentage of Faults Detected (APFD) for original order, random order (mean of 100 iterations), and LLM-prioritized runs against the 14-fault matrix, along with early fault detection percentages.*

3. **Evaluate Ranking Stability**
   ```bash
   python evaluation/stability.py
   ```
   *Measures ranking consistency across the 5 LLM runs using pairwise Kendall tau rank correlation coefficients.*

4. **Weight Sensitivity Analysis**
   ```bash
   python evaluation/weight_sensitivity.py
   ```
   *Evaluates the robustness of prioritization rankings and APFD performance when varying risk attribute weights across four distinct weight profiles.*

5. **Risk Model Comparison**
   ```bash
   python evaluation/risk_model_comparison.py
   ```
   *Compares fault-detection effectiveness (APFD) between the linear additive risk formula and a two-factor multiplicative (Impact × Likelihood) model.*

---

## 3. Visualization

To generate the APFD comparison chart:

```bash
pip install matplotlib
python evaluation/make_chart.py
```
*Generates and saves `apfd_chart.png`, a publication-ready bar chart comparing original order, random order, and the 5-run LLM-assisted mean with range bars.*

---

## Benchmark Values Reference

- **Original Order APFD**: 0.540
- **Random Order APFD (mean of 100)**: 0.557
- **LLM-Assisted APFD**: Mean 0.548 (range: 0.524 – 0.574)
- **Mean Kendall tau**: 0.779 (range: 0.669 – 0.894)
- **Weight Profiles (APFD means)**: Default: 0.548 | Equal: 0.540 | Impact-heavy: 0.540 | Likelihood-heavy: 0.542
- **Risk Formulas (APFD means)**: Additive: 0.548 | Multiplicative: 0.558
