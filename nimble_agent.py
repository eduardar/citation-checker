import os, json, time
from dotenv import load_dotenv
from nimble_python import Nimble

load_dotenv()
nimble = Nimble(api_key=os.environ.get("NIMBLE_API_KEY"))

def _start_run(question, effort):
    try:
        run = nimble.agents.run(input=question, effort=effort)
        return run, run.web_search_agent_id
    except TypeError:
        # agents.run didn't accept effort: create an agent with it, then start a run
        agent = nimble.agents.create(display_name="citation-checker", effort=effort)
        run = nimble.agents.runs.create(agent.id, input=question, effort=effort)
        return run, agent.id

def ask_agent(question: str, effort: str = "low") -> dict:
    run, agent_id = _start_run(question, effort)
    print(f"Run started ({effort}), waiting...")
    while run.is_active:
        time.sleep(5)
        run = nimble.agents.runs.get(run.id, agent_id=agent_id)
        print(f"  status: {run.status}")
    if run.status != "completed":
        raise RuntimeError(f"Run ended as {run.status}")

    out = nimble.agents.runs.result(run.id, agent_id=agent_id).output
    sources, nimble_claims = {}, []
    for cl in out.trust.claims:
        urls = [c.url for c in cl.citations]
        if urls:
            sources[str(cl.callout)] = urls[0]
        nimble_claims.append({
            "callout": str(cl.callout),
            "confidence": cl.confidence,
            "urls": urls,
            "excerpts": [e for c in cl.citations for e in (c.excerpts or [])],
        })
    return {"question": question, "answer": out.content, "sources": sources,
            "nimble_confidence": out.trust.confidence, "nimble_claims": nimble_claims}

if __name__ == "__main__":
    q = "When was the Eiffel Tower built, how tall is it, and who designed it?"
    ex = ask_agent(q)
    json.dump(ex, open("agent_example.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\nANSWER:\n", ex["answer"])
    print("\nSOURCES:", json.dumps(ex["sources"], indent=2))
    print("\nNimble overall confidence:", ex["nimble_confidence"])