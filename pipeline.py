from concurrent.futures import ThreadPoolExecutor
from claims import split_claims
from fetch import fetch_text
from judge import judge

def _judge_one(c, texts):
    if not c["citations"]:
        return {**c, "verdict": "no_citation", "evidence": "",
                "reason": "No source cited", "evidence_verified": False}
    src = "\n\n".join(texts.get(n, "") for n in c["citations"])
    result = {**c, **judge(c["claim"], src)}
    print(f"  judged: {c['claim'][:60]}")
    return result

def check(answer: str, sources: dict) -> list[dict]:
    texts = {k: fetch_text(u) for k, u in sources.items()}
    claims = split_claims(answer)
    print(f"{len(claims)} claims, judging...")
    with ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(lambda c: _judge_one(c, texts), claims))

# def check(answer: str, sources: dict) -> list[dict]:
#     texts = {k: fetch_text(u) for k, u in sources.items()}
#     results = []
#     for c in split_claims(answer):
#         if not c["citations"]:
#             results.append({**c, "verdict": "no_citation", "evidence": "",
#                             "reason": "No source cited", "evidence_verified": False})
#             continue
#         src = "\n\n".join(texts.get(n, "") for n in c["citations"])
#         results.append({**c, **judge(c["claim"], src)})
#     return results