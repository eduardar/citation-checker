# Citation Checker

**Does each cited source actually support the claim?**

AI answer engines attach citations to their answers, but a citation is only useful if the page really says what the answer claims. Citation Checker takes an AI answer with `[n]` citations, fetches every cited page live, splits the answer into atomic claims, and checks each claim against the source it cites, quoting the evidence.

It can also audit a **Nimble Web Search Agent** end to end: ask a question, get Nimble's cited answer and its own confidence grades, then independently verify every citation.

Built solo in one day at the AI Engineer NYC Hackathon (October 11, 2026).

![Score and a supported claim](images/demo.png)

## How it works

1. **Answer** (optional): a Nimble Web Search Agent answers a question with `[n]` citations and a per-claim confidence grade (`effort="low"`, about 15 seconds).
2. **Fetch**: Nimble Extract fetches the live text of each cited page (with JavaScript rendering), cleaned with `trafilatura` and cached locally.
3. **Split**: Gemini breaks the answer into atomic, self-contained claims, keeping each claim's citation numbers and qualifiers ("himself", "only", "about").
4. **Judge**: Gemini labels each claim `supported` / `partial` / `contradicted` / `not_found`, using only the source text, and quotes the sentence it relied on.
5. **Verify the judge**: code checks that the quoted evidence actually appears in the source. Pages that could not be fetched properly (too short, or identical text returned for different URLs) are marked `unverifiable` instead of blaming the source.

The Streamlit app has three modes: ask a Nimble agent and audit its answer live, check a pasted answer, or replay a saved run.

## What I found

### 1. Planted errors are caught, with verifiable evidence
On a hand-written answer about the Eiffel Tower with three planted errors (450 m tall, "designed by Gustave Eiffel himself", "about 5 million visitors"), all three were marked `contradicted`, the true claims were `supported`, and every quoted piece of evidence was found verbatim in the source.

### 2. Auditing a Nimble agent: right answers, imperfect citations
Two live runs of the same question ("When was the Eiffel Tower built, how tall is it, and who designed it?"):

| Run | Nimble's confidence | Claims | Supported by their citation | Could not verify |
| --- | --- | --- | --- | --- |
| A | high (all claims) | 23 | 15 of 18 verifiable | 5 |
| B | medium (all claims) | 18 | 10 of 15 verifiable | 3 |

The same question produced a different answer, different sources (9 vs. 10) and a different confidence grade, which is a good argument for auditing every answer rather than trusting a single run.

Notable cases:
- **Right answer, stale citation.** The answer said 330 m (correct since 2022), but one cited page (WorldAtlas) says 324 m including antennas, an outdated figure. Nimble rated that citation high confidence.
- **Source labels.** In run A, all 9 sources were labeled `official`, including a travel site and Wikipedia.
- **Fetch failures look like "not found".** One page returned 41 characters (blocked), and two different pages on the official site returned the same 4,545-character template. Before adding the `unverifiable` status, 5 of 6 "not found" verdicts came from these pages, not from the answer.

![A partial verdict](images/partial.png)

### 3. The judge itself is unreliable in specific ways
- **Too lenient:** "the tower was the *entrance arch* of the fair" was `supported` by a sentence saying it was the *centrepiece*.
- **Too literal:** "1,083 feet" was `contradicted` because the source says 1,082 feet, a unit-conversion rounding difference (330 m ≈ 1,082.7 ft).
- **Verdict contradicts its own reasoning:** "Eiffel climbed the 1,710 steps on the day of completion" was labeled `contradicted`, while the judge's explanation says Eiffel did climb on foot that day. `partial` would be the right label, since the source gives the 1,710 steps for visitors.

![Verdict inconsistent with its own reasoning](images/judge_inconsistency.png)

### 4. Judge stability (small pilot)
Same claims and sources; only the judge changes (repeat run, three prompt wordings, and a stronger model). On the 6 claims of the planted example:
- The fast model (`gemini-3.5-flash-lite`) agreed with itself 100% across a repeat run and three prompt wordings.
- The stronger model (`gemini-3.8-flash`) disagreed on exactly one claim, the ambiguous "entrance arch", marking it `partial`. (One stronger-model call failed on quota and was excluded.)
- On real agent answers, a borderline claim ("designed by a team led by Eiffel") flipped from `not_found` to `partial` between two runs with identical inputs.

Takeaway: **a stable judge is not necessarily an accurate one.** The fast judge was consistently lenient on the one ambiguous claim, and instability concentrates on borderline claims, where the verdict matters most. Even the claim splitter varies (21 vs. 23 claims for the same answer).

This is a small pilot (6 planted claims plus two agent runs), not a benchmark.

## Engineering notes
- Gemini free tier: 15 requests/minute on the fast model and 20/day on the stronger one, plus 503/504 errors under load. Handled with retries and backoff, a 3-minute timeout, page caching, and the fast model as the default.
- Every live run is saved (`last_run.json`), and a protected demo run (`demo_run.json`) can be replayed instantly.
- Nimble's per-claim `excerpts` came back empty at `effort="low"`, so auditing Nimble's own quotes is left for future work.

## Related work
Nimble's cookbook [Fact-check documents with LiteLLM and Nimble](https://www.nimbleway.com/cookbooks/fact-check-documents-with-litellm) searches for **new** evidence for each claim. Citation Checker instead checks whether the **citations an answer already gave** hold up, audits the agent's own confidence grades, and tests whether the judge itself is reliable.

## Next steps
- More answers and human labels, to measure judge accuracy, not just agreement.
- A coherence check that flags verdicts contradicting their own reasoning.
- Trim each page to the passage relevant to the claim (fewer tokens, fewer rate-limit hits).
- Audit Nimble's verbatim excerpts at higher effort levels.

## Run it
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
pip install -r requirements.txt
```
Create a `.env` file:
```
GEMINI_API_KEY=...
NIMBLE_API_KEY=...
```
Then:
```bash
streamlit run app.py
```

| File | What it does |
| --- | --- |
| `app.py` | Streamlit interface (live agent audit, pasted answer, saved run) |
| `nimble_agent.py` | Runs a Nimble Web Search Agent and returns answer, sources and confidence |
| `fetch.py` | Fetches cited pages with Nimble Extract, with a cache and a fallback |
| `claims.py` | Splits an answer into atomic claims |
| `judge.py` | Labels each claim against its source and verifies the quoted evidence |
| `pipeline.py` | Runs the full check, flagging unreadable sources |
| `stability.py`, `prompts.py` | Judge stability analysis across prompts and models |
| `audit_agent.py` | Compares our verdicts with Nimble's confidence for a saved agent run |
