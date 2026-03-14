"""
Module M7: Symptom–Disease Mapping Database
Frontend Dashboard – Phase 1: Display Only
"""

import streamlit as st
import pandas as pd
from database.connection import get_collections, test_connection

st.set_page_config(
    page_title="M7 – Symptom–Disease Mapping",
    page_icon="🏥",
    layout="wide",
)

# styling
st.markdown("""
<style>
    .main-title { font-size:2rem; font-weight:700; color:#1e3a5f; }
    .sub-title  { font-size:0.95rem; color:#666; margin-top:-8px; }
    .badge      { background:#e8f0fe; color:#1a56db; border-radius:6px;
                  padding:3px 10px; font-size:0.85rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏥 Module M7: Symptom–Disease Mapping Database</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Category B · IIT(ISM) DBMS Project 2025–26</div>', unsafe_allow_html=True)
st.markdown("---")

# DB connection
if not test_connection():
    st.error(" MongoDB connection failed. Check `.streamlit/secrets.toml`.")
    st.stop()

cols = get_collections()

# tabs
tab_home, tab_symptoms, tab_diseases, tab_assoc, tab_rules = st.tabs([
    " Home",
    " Symptoms",
    " Diseases",
    " Associations",
    " Diagnosis Rules",
])

# HOME
with tab_home:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("###  About this Module")
        st.markdown("""
**Module M7** is part of Category B: Symptom–Disease Diagnosis Support.

**Primary Objectives:**
- Design a comprehensive symptom-disease relationship database
- Implement weighted association strength calculations
- Create a Bayesian diagnostic probability engine
- Develop a differential diagnosis generation system

**Technical Specifications:**
- **Entities:** Symptom · Disease · SymptomDiseaseAssociation · DiagnosisRule
- **Data Sources:** ICD-11 (WHO) · SNOMED-CT (International Edition)
- **Association Metrics:** Sensitivity · Specificity · Likelihood Ratios (LR+, LR−)
        """)

        st.markdown("###  Module Dependencies")
        st.markdown("""
| Direction | Modules |
|---|---|
| Depends on | **M1** – Patient Demographics |
| Feeds into | **M8** Fever · **M9** Respiratory · **M10** GI · **M11** Neuro · **M12** Rule Ranking |
| Also feeds | **M13** Clinical Query · **M19** Drug Interaction |
        """)

    with col2:
        st.markdown("###  Live Stats")
        for label, key in [
            ("Symptoms",     "symptoms"),
            ("Diseases",     "diseases"),
            ("Associations", "symptom_disease_associations"),
            ("Rules",        "diagnosis_rules"),
        ]:
            st.metric(label, cols[key].count_documents({}))

# SYMPTOMS
with tab_symptoms:
    st.markdown("###  Symptoms Collection")
    st.caption("Source: SNOMED-CT International Edition")

    data = list(cols["symptoms"].find({}, {"_id": 0}))
    if data:
        df = pd.DataFrame(data)

        # Filter by body system
        systems = ["All"] + sorted(df["body_system"].unique().tolist())
        selected = st.selectbox("Filter by body system", systems)
        if selected != "All":
            df = df[df["body_system"] == selected]

        st.dataframe(df, use_container_width=True, height=420)
        st.caption(f"Showing **{len(df)}** of **{len(data)}** symptoms")
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")

# DISEASES
with tab_diseases:
    st.markdown("###  Diseases Collection")
    st.caption("Source: ICD-11 MMS 2024-01 (WHO)")

    data = list(cols["diseases"].find({}, {"_id": 0}))
    if data:
        df = pd.DataFrame(data).sort_values("prevalence_rate", ascending=False)
        st.dataframe(df, use_container_width=True, height=420)
        st.caption(f"**{len(df)}** diseases · sorted by prevalence rate (descending)")

        # Simple bar chart
        st.markdown("##### Prevalence Rate")
        st.bar_chart(df.set_index("disease_name")["prevalence_rate"])
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")

# ASSOCIATIONS
with tab_assoc:
    st.markdown("###  Symptom–Disease Associations")
    st.caption("Sensitivity · Specificity · Likelihood Ratios from peer-reviewed clinical literature")

    data = list(cols["symptom_disease_associations"].find({}, {"_id": 0}))
    if data:
        df = pd.DataFrame(data)

        # Enrich with names
        sym_map = {s["symptom_id"]: s["symptom_name"]
                   for s in cols["symptoms"].find({}, {"_id": 0})}
        dis_map = {d["disease_id"]: d["disease_name"]
                   for d in cols["diseases"].find({}, {"_id": 0})}

        df.insert(1, "symptom_name", df["symptom_id"].map(sym_map))
        df.insert(3, "disease_name", df["disease_id"].map(dis_map))

        # Filter by disease
        diseases = ["All"] + sorted(dis_map.values())
        selected = st.selectbox("Filter by disease", diseases)
        if selected != "All":
            df = df[df["disease_name"] == selected]

        st.dataframe(df, use_container_width=True, height=420)
        st.caption(f"Showing **{len(df)}** associations")
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")

# DIAGNOSIS RULES
with tab_rules:
    st.markdown("###  Diagnosis Rules Collection")
    st.caption("Rule-based inference engine data — clinical decision criteria")

    data = list(cols["diagnosis_rules"].find({}, {"_id": 0}))
    if data:
        dis_map = {d["disease_id"]: d["disease_name"]
                   for d in cols["diseases"].find({}, {"_id": 0})}
        sym_map = {s["symptom_id"]: s["symptom_name"]
                   for s in cols["symptoms"].find({}, {"_id": 0})}

        # Build display-friendly rows
        rows = []
        for r in data:
            sym_names = [sym_map.get(sid, sid) for sid in r["symptom_combination"]]
            rows.append({
                "rule_id":            r["rule_id"],
                "rule_name":          r["rule_name"],
                "symptom_combination": ", ".join(sym_names),
                "suggested_disease":  dis_map.get(r["suggested_disease_id"], r["suggested_disease_id"]),
                "confidence_modifier": r["confidence_modifier"],
                "priority":           r["priority"],
            })

        df = pd.DataFrame(rows).sort_values("priority")
        st.dataframe(df, use_container_width=True, height=450)
        st.caption(f"**{len(df)}** rules · sorted by priority")
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")
