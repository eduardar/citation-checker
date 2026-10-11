from judge import PROMPT as BASE
from llm import FAST_MODEL, SMART_MODEL

REWORDED = """Decide whether the SOURCE backs up the CLAIM. Rely strictly on the SOURCE; ignore anything you already know.

Labels:
- "not_found": the SOURCE never addresses the claim.
- "contradicted": the SOURCE says something incompatible with the claim.
- "partial": the SOURCE backs up only part of the claim, or is less specific.
- "supported": the SOURCE plainly confirms the claim.

Output JSON: {{"verdict": "...", "evidence": "exact sentence from the SOURCE, or empty", "reason": "one sentence"}}

CLAIM: {claim}

SOURCE:
{source}"""

REASON_FIRST = """You check whether a SOURCE supports a CLAIM, using ONLY the source text.
First reason step by step about what the source says, then quote the best evidence, then decide.
Verdict options: "supported", "partial", "contradicted", "not_found".

Return JSON in this order: {{"reason": "your reasoning", "evidence": "exact sentence from the source, or empty", "verdict": "..."}}

CLAIM: {claim}

SOURCE:
{source}"""

# name -> (prompt, model)
VARIANTS = {
    "base":         (BASE, FAST_MODEL),
    "base_repeat":  (BASE, FAST_MODEL),   # same setup again: measures random noise
    "reworded":     (REWORDED, FAST_MODEL),
    "reason_first": (REASON_FIRST, FAST_MODEL),
    "base_smart":   (BASE, SMART_MODEL),  # same prompt, stronger model
}