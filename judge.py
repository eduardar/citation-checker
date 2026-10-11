from llm import ask_json

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

def judge(claim: str, source_text: str, prompt: str = PROMPT) -> dict:
    result = ask_json(prompt.format(claim=claim, source=source_text))
    ev = (result.get("evidence") or "").strip()
    result["evidence_verified"] = bool(ev) and ev in source_text
    return result