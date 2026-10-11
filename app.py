import json
import streamlit as st
from pipeline import check

ICONS = {"supported": "🟢", "partial": "🟡", "contradicted": "🔴",
         "not_found": "🟠", "no_citation": "⚪"}
COLORS = {"supported": "green", "partial": "orange", "contradicted": "red",
          "not_found": "orange", "no_citation": "gray"}

st.set_page_config(page_title="Citation Checker", page_icon="🔎")
st.title("🔎 Citation Checker")
st.caption("Does each cited source actually support the claim? Sources fetched live with Nimble, judged with Gemini.")

ex = json.load(open("example.json", encoding="utf-8"))
answer = st.text_area("AI answer (with [n] citations)", ex["answer"], height=140)
sources = st.text_area("Sources (JSON: citation number → URL)",
                       json.dumps(ex["sources"], indent=2), height=110)

if st.button("Check citations", type="primary"):
    with st.spinner("Fetching sources and judging claims..."):
        results = check(answer, json.loads(sources))

    ok = sum(r["verdict"] == "supported" for r in results)
    st.metric("Groundedness", f"{ok}/{len(results)} claims supported")

    for r in results:
        icon = ICONS.get(r["verdict"], "⚪")
        with st.container(border=True):
            color = COLORS.get(r["verdict"], "gray")
            st.markdown(f"{icon} **{r['claim']}** — :{color}[**{r['verdict']}**] · cites {r['citations']}")
            if r.get("evidence"):
                flag = "" if r.get("evidence_verified") else "  ⚠️ quote not found in source"
                st.markdown(f"> {r['evidence']}{flag}")
            st.caption(r.get("reason", ""))