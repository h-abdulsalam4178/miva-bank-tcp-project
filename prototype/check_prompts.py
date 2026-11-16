import json

with open("run_logs/runs.jsonl", encoding="utf-8") as file:
    runs = [json.loads(line) for line in file if line.strip()]

print("Same model:", runs[0]["model"] == runs[1]["model"])
print("Same prompt:", runs[0]["prompt"] == runs[1]["prompt"])
print("Prompt lengths:", len(runs[0]["prompt"]), len(runs[1]["prompt"]))