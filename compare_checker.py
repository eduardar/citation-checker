import json
import pandas as pd

labels = pd.read_csv("labels.csv")
results = json.load(open("demo_run.json", encoding="utf-8"))["results"]

# What the checker thinks the verdict should be (only for rows it actually checked)
checker = {}
for r in results:
    if "coherent" in r:  # the check ran on this row
        checker[r["claim"]] = r["verdict"] if r["coherent"] else r["implied_verdict"]

df = labels[labels["claim"].isin(checker)].copy()
df["checker_says"] = df["claim"].map(checker)

pd.set_option("display.width", 200, "display.max_colwidth", 55)
print(df[["claim", "judge_verdict", "checker_says", "my_label"]].to_string(index=False))

n = len(df)
print(f"\nOn the {n} rows the checker reviewed:")
print(f"  judge   matches my label: {(df['judge_verdict'] == df['my_label']).sum()}/{n}")
print(f"  checker matches my label: {(df['checker_says'] == df['my_label']).sum()}/{n}")