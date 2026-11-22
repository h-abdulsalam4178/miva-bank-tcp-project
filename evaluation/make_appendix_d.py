import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "prototype", "run_logs", "runs.jsonl")
OUT = os.path.join(HERE, "appendix_d.txt")

with open(LOG, encoding="utf-8") as file:
    runs = [json.loads(line) for line in file if line.strip()]

official = [r for r in runs
            if r.get("prompt_version") == "v1.0" and r["time"] >= "2026-11-17"]
run = official[0]

prompt = run["prompt"]
short_prompt = (prompt[:700]
                + "\n[... middle of the prompt omitted: context documents and test cases ...]\n"
                + prompt[-500:])

reply = json.loads(run["raw_response"])
short_reply = json.dumps(reply[:2], indent=2, ensure_ascii=False)

text = (
    "Run-log entry (official run 1 of 5)\n"
    f"time: {run['time']}\n"
    f"model: {run['model']}\n"
    f"prompt_version: {run['prompt_version']}\n"
    f"temperature: {run.get('temperature', 'default (not set)')}\n\n"
    "prompt (shortened):\n" + short_prompt + "\n\n"
    f"raw_response (first 2 of {len(reply)} test objects):\n" + short_reply + "\n"
)

with open(OUT, "w", encoding="utf-8") as file:
    file.write(text)
print(text)