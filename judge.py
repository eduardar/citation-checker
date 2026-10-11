from llm import ask_json, FAST_MODEL

PROMPT = """You check whether a SOURCE supports a CLAIM.
Use ONLY the source text. Never use your own knowledge, even if you know the answer.

Verdict (pick one):
- "supported": the source clearly states this.
- "partial": the source supports part of it, or states it less precisely.
- "contradicted": the source states something different (e.g. a different number or person).
- "not_found": the source does not address this.

Return JSON: {{"verdict": "...", "evidence": "sentence copied exactly from the source, or empty", "reason": "one sentence"}}

CLAIM: {claim}

SOURCE:
{source}"""

COHERENCE_PROMPT = """A fact-checking judge gave a VERDICT and a REASON for a CLAIM.
Does the REASON actually justify the VERDICT?
Verdict options: "supported", "partial", "contradicted", "not_found".

Return JSON: {{"consistent": true or false, "implied_verdict": "the verdict the REASON actually supports"}}

CLAIM: {claim}
VERDICT: {verdict}
REASON: {reason}"""

def check_coherence(r: dict) -> dict:
    if r["verdict"] in ("supported", "unverifiable", "no_citation"):
        return r
    out = ask_json(COHERENCE_PROMPT.format(claim=r["claim"], verdict=r["verdict"],
                                           reason=r.get("reason", "")))
    r["coherent"] = bool(out.get("consistent", True))
    r["implied_verdict"] = out.get("implied_verdict", r["verdict"])
    return r

def judge(claim: str, source_text: str, prompt: str = PROMPT, model: str = FAST_MODEL) -> dict:
    result = ask_json(prompt.format(claim=claim, source=source_text), model=model)
    ev = (result.get("evidence") or "").strip()
    result["evidence_verified"] = bool(ev) and ev in source_text
    return result