import json
from claims import split_claims

ex = json.load(open("example.json", encoding="utf-8"))
claims = split_claims(ex["answer"])
for c in claims:
    print(c["citations"], "-", c["claim"])
print(f"\n{len(claims)} claims")