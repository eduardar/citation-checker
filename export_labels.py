import json, csv

rows = []
for r in json.load(open("demo_run.json", encoding="utf-8"))["results"]:
    rows.append({
        "set": "agent",
        "claim": r["claim"],
        "citations": " ".join(r["citations"]),
        "judge_verdict": r["verdict"],
        "evidence": r.get("evidence", ""),
        "reason": r.get("reason", ""),
        "coherence_flag": {True: "coherent", False: "FLAGGED"}.get(r.get("coherent"), "not checked"),
        "my_label": "",
    })

with open("labels.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} claims exported to labels.csv")