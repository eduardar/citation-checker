import json, os
import streamlit as st
from pipeline import check

ICONS = {"supported": "🟢", "partial": "🟡", "contradicted": "🔴", "not_found": "🟠",
         "unverifiable": "⚫", "no_citation": "⚪"}
COLORS = {"supported": "green", "partial": "orange", "contradicted": "red", "not_found": "orange",
          "unverifiable": "gray", "no_citation": "gray"}

st.set_page_config(page_title="Citation Checker", page_icon="🔎")
st.title("🔎 Citation Checker")
st.caption("Does each cited source actually support the claim? Live pages via Nimble, judged by Gemini.")

def show(results, nimble_conf=None):
    verifiable = [r for r in results if r["verdict"] not in ("unverifiable", "no_citation")]
    ok = sum(r["verdict"] == "supported" for r in verifiable)
    c1, c2 = st.columns(2)
    c1.metric("Supported by their citation", f"{ok}/{len(verifiable)} verifiable claims")
    c2.metric("Could not verify", len(results) - len(verifiable))
    for r in results:
        color = COLORS.get(r["verdict"], "gray")
        with st.container(border=True):
            line = f"{ICONS.get(r['verdict'], '⚪')} **{r['claim']}** — :{color}[**{r['verdict']}**] · cites {r['citations']}"
            if nimble_conf:
                line += " · Nimble: " + ", ".join(nimble_conf.get(n, "?") for n in r["citations"])
            st.markdown(line)
            if r.get("evidence"):
                flag = "" if r.get("evidence_verified") else "  ⚠️ quote not found in source"
                st.markdown(f"> {r['evidence']}{flag}")
            st.caption(r.get("reason", ""))

mode = st.radio("Mode", ["Ask a Nimble agent", "Check a pasted answer", "Load saved demo run"],
                horizontal=True)

if mode == "Ask a Nimble agent":
    q = st.text_input("Question", "When was the Eiffel Tower built, how tall is it, and who designed it?")
    if st.button("Ask & audit", type="primary"):
        from nimble_agent import ask_agent
        with st.spinner("Nimble agent researching (low effort, ~15s)..."):
            ex = ask_agent(q)
        st.markdown(ex["answer"].split("Source index:")[0])
        conf = {c["callout"]: c["confidence"] for c in ex["nimble_claims"]}
        with st.spinner("Auditing every citation..."):
            results = check(ex["answer"].split("Source index:")[0].split("\n---")[0], ex["sources"])
        json.dump({"ex": ex, "results": results}, open("last_run.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        show(results, conf)

elif mode == "Check a pasted answer":
    ex = json.load(open("example.json", encoding="utf-8"))
    answer = st.text_area("AI answer (with [n] citations)", ex["answer"], height=140)
    sources = st.text_area("Sources (JSON: citation number → URL)", json.dumps(ex["sources"], indent=2))
    if st.button("Check citations", type="primary"):
        with st.spinner("Fetching sources and judging claims..."):
            show(check(answer, json.loads(sources)))

else:
    path = "demo_run.json" if os.path.exists("demo_run.json") else "last_run.json"
    if os.path.exists(path):
        saved = json.load(open(path, encoding="utf-8"))
        st.info(f"Saved run for: {saved['ex']['question']}")
        st.text_input("Question", saved["ex"]["question"], disabled=True)
        st.markdown(saved["ex"]["answer"].split("Source index:")[0])
        conf = {c["callout"]: c["confidence"] for c in saved["ex"]["nimble_claims"]}
        show(saved["results"], conf)
    else:
        st.warning("No saved run yet. Do one live run first.")