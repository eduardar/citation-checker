from concurrent.futures import ThreadPoolExecutor
from claims import split_claims
from fetch import fetch_text
from judge import judge

MIN_CHARS = 500

def fetch_sources(sources: dict):
    """Fetch every source and flag the ones that didn't really download."""
    texts = {k: fetch_text(u) for k, u in sources.items()}
    urls_by_text = {}
    for k, t in texts.items():
        urls_by_text.setdefault(t, set()).add(sources[k])
    bad = {k for k, t in texts.items()
           if len(t) < MIN_CHARS or len(urls_by_text[t]) > 1}  # too short, or same text as another URL
    return texts, bad

def _judge_one(c, texts, bad):
    cited = c["citations"]
    if not cited:
        return {**c, "verdict": "no_citation", "evidence": "", "reason": "No source cited",
                "evidence_verified": False}
    good = [n for n in cited if n in texts and n not in bad]
    if not good:
        return {**c, "verdict": "unverifiable", "evidence": "",
                "reason": "Cited page(s) could not be fetched properly", "evidence_verified": False}
    src = "\n\n".join(texts[n] for n in good)
    r = {**c, **judge(c["claim"], src)}
    if r["verdict"] == "not_found" and len(good) < len(cited):
        r["verdict"] = "unverifiable"  # some cited pages were unreadable: don't blame the source
        r["reason"] += " (some cited pages could not be fetched)"
    print(f"  judged: {c['claim'][:60]}")
    return r

def check(answer: str, sources: dict) -> list[dict]:
    texts, bad = fetch_sources(sources)
    if bad:
        print(f"Unreadable sources: {sorted(bad)}")
    claims = split_claims(answer)
    print(f"{len(claims)} claims, judging...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda c: _judge_one(c, texts, bad), claims))