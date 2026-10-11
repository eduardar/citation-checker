import json
from pipeline import check

ex = json.load(open("example.json", encoding="utf-8"))
for r in check(ex["answer"], ex["sources"]):
    print(f"{r['verdict'].upper():13} {r['claim']}")
    print(f"   evidence: {r['evidence'][:150]}  (verified: {r['evidence_verified']})")
    print(f"   reason:   {r['reason']}\n")