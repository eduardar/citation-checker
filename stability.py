import json, itertools
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from claims import split_claims
from fetch import fetch_text
from judge import judge
from prompts import VARIANTS

def load_claims(examples):
    """Split each answer ONCE, so every variant judges the exact same claims."""
    rows = []
    for ex in examples:
        texts = {k: fetch_text(u) for k, u in ex["sources"].items()}
        for c in split_claims(ex["answer"]):
            if c["citations"]:
                src = "\n\n".join(texts.get(n, "") for n in c["citations"])
                rows.append({"claim": c["claim"], "source": src})
    return rows

def run_one(row, name):
    prompt, model = VARIANTS[name]
    try:
        return judge(row["claim"], row["source"], prompt=prompt, model=model)["verdict"]
    except Exception as e:
        print(f"  error ({name}): {e}")
        return "error"

def main():
    examples = [json.load(open("example.json", encoding="utf-8"))]
    claims = load_claims(examples)
    names = list(VARIANTS)
    print(f"{len(claims)} claims x {len(names)} variants")

    jobs = [(i, n) for i in range(len(claims)) for n in names]
    with ThreadPoolExecutor(max_workers=3) as pool:
        verdicts = list(pool.map(lambda j: run_one(claims[j[0]], j[1]), jobs))

    df = pd.DataFrame([{"claim": c["claim"]} for c in claims])
    for (i, n), v in zip(jobs, verdicts):
        df.loc[i, n] = v
    valid = df[names].replace("error", pd.NA)
    df["stable"] = valid.nunique(axis=1, dropna=True) == 1

    pd.set_option("display.width", 200, "display.max_colwidth", 60)
    print(df[["claim"] + names].to_string())
    print(f"\nVerdict changed for {(~df['stable']).sum()} of {len(df)} claims (errors ignored)")
    for a, b in itertools.combinations(names, 2):
        ok = (df[a] != "error") & (df[b] != "error")
        if ok.sum():
            print(f"{a:13} vs {b:13}: {(df.loc[ok, a] == df.loc[ok, b]).mean():.0%} agreement (n={ok.sum()})")
    df.to_csv("stability.csv", index=False)

if __name__ == "__main__":
    main()