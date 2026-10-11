from llm import ask_json

PROMPT = """Split the answer below into atomic, verifiable claims.
Rules:
- Each claim contains exactly ONE fact (one number, one date, or one relation).
- Rewrite each claim so it makes sense on its own (replace "it"/"the tower" with the full name).
- Keep the citation number(s) from the sentence the claim came from, e.g. ["1"]. If none, use [].
- Include the original sentence the claim came from.
- Preserve qualifiers exactly: words like "himself", "only", "first", "about", "most" change the meaning.
- Name entities fully, including years (e.g. "the 1889 World's Fair", not "the World's Fair").

Return a JSON list: [{{"claim": "...", "citations": ["1"], "sentence": "..."}}]

Answer:
{answer}"""

def split_claims(answer: str) -> list[dict]:
    return ask_json(PROMPT.format(answer=answer))