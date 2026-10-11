# Citation Checker

Checks whether an AI answer's citations actually support its claims.

![demo](demo.png)

## How it works
1. **Fetch**: Nimble extracts the live text of each cited page.
2. **Split**: Gemini breaks the answer into atomic, self-contained claims.
3. **Judge**: Gemini labels each claim supported / partial / contradicted / not_found,
   quoting evidence from the source. Code verifies the quote actually exists in the source.

## Judge stability (pilot)
Same claims, same sources; only the judge changes (prompt wording, repeat run, model).
- Prompt wording and repeated runs: 100% agreement on 6 claims.
- On the one ambiguous claim ("entrance arch" vs. source's "centrepiece"), the fast
  model said *supported* in all 4 runs; a stronger model said *partial*.
- Takeaway: a stable judge isn't necessarily an accurate one.

Small pilot (6 claims). Next: more ambiguous claims, human labels.

## Run it
pip install -r requirements.txt
streamlit run app.py