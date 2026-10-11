import pandas as pd

df = pd.read_csv("labels.csv")
df = df[df["my_label"].notna() & (df["judge_verdict"] != "unverifiable")]
acc = (df["judge_verdict"] == df["my_label"]).mean()
print(f"Judge agrees with my labels on {acc:.0%} of {len(df)} verifiable claims\n")
print(pd.crosstab(df["my_label"], df["judge_verdict"], rownames=["human"], colnames=["judge"]))

flagged = df[df["coherence_flag"] == "FLAGGED"]
if len(flagged):
    wrong = (flagged["judge_verdict"] != flagged["my_label"]).sum()
    print(f"\nCoherence flags: {wrong} of {len(flagged)} flagged verdicts were actually wrong")