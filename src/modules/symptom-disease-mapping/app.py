"""
Module M7: Symptom–Disease Mapping Database
Streamlit frontend – calls the FastAPI backend (api/main.py) via HTTP.
Start the backend first: uvicorn api.main:app --reload
Then start this:        streamlit run app.py
"""

import streamlit as st
import pandas as pd
import requests

API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000")


def api(method: str, path: str, **kwargs):
    url = f"{API_BASE}{path}"
    resp = getattr(requests, method)(url, **kwargs)
    resp.raise_for_status()
    return resp.json()


st.set_page_config(
    page_title="M7 – Symptom–Disease Mapping",
    page_icon="🏥",
    layout="wide",
)

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

try:
    api("get", "/health")
except Exception:
    st.error(
        "⚠️ Cannot reach the FastAPI backend at `http://127.0.0.1:8000`. "
        "Start it with: `uvicorn api.main:app --reload`"
    )
    st.stop()

# Tabs
tab_home, tab_symptoms, tab_diseases, tab_assoc, tab_rules, tab_engine, tab_queries, tab_crud = st.tabs([
    " Home",
    " Symptoms",
    " Diseases",
    " Associations",
    " Diagnosis Rules",
    " Diagnostic Engine",
    " SQL Queries",
    " CRUD Operations",
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
        try:
            stats = api("get", "/stats")
            st.metric("Symptoms",     stats["symptoms"])
            st.metric("Diseases",     stats["diseases"])
            st.metric("Associations", stats["associations"])
            st.metric("Rules",        stats["diagnosis_rules"])
        except Exception as e:
            st.error(f"Could not load stats: {e}")

# SYMPTOMS
with tab_symptoms:
    st.markdown("###  Symptoms Collection")
    st.caption("Source: SNOMED-CT International Edition")

    data = api("get", "/symptoms")
    if data:
        df = pd.DataFrame(data)
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

    data = api("get", "/diseases")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=420)
        st.caption(f"**{len(df)}** diseases · sorted by prevalence rate (descending)")

        st.markdown("##### Prevalence Rate")
        st.bar_chart(df.set_index("disease_name")["prevalence_rate"])
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")

# ASSOCIATIONS
with tab_assoc:
    st.markdown("###  Symptom–Disease Associations")
    st.caption("Sensitivity · Specificity · Likelihood Ratios from peer-reviewed clinical literature")

    data = api("get", "/associations")
    if data:
        df = pd.DataFrame(data)
        all_disease_names = ["All"] + sorted(df["disease_name"].dropna().unique().tolist())
        selected = st.selectbox("Filter by disease", all_disease_names)
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

    data = api("get", "/diagnosis-rules")
    if data:
        rows = []
        for r in data:
            rows.append({
                "rule_id":             r["rule_id"],
                "rule_name":           r["rule_name"],
                "symptom_combination": ", ".join(r["symptom_combination"]),
                "suggested_disease":   r["suggested_disease"],
                "confidence_modifier": r["confidence_modifier"],
                "priority":            r["priority"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, height=450)
        st.caption(f"**{len(df)}** rules · sorted by priority")
    else:
        st.warning("No data. Run `python data/populate_all.py` first.")

# DIAGNOSTIC ENGINE
with tab_engine:
    st.markdown("### 🧠 Bayesian Diagnostic Engine")
    st.caption("Generate a Differential Diagnosis based on Posterior Probability.")

    # Fetch symptom list for the multi-select
    all_symptoms = api("get", "/symptoms")
    sym_name_to_id = {s["symptom_name"]: s["symptom_id"] for s in all_symptoms}

    selected_symptom_names = st.multiselect(
        "Select Patient Symptoms (Pattern Recognition & Combos):",
        options=list(sym_name_to_id.keys()),
        default=[],
    )

    if st.button("Generate Differential Diagnosis", type="primary"):
        if not selected_symptom_names:
            st.warning("Please select at least one symptom.")
        else:
            with st.spinner("Calculating Bayesian Posteriors..."):
                symptom_ids = [sym_name_to_id[name] for name in selected_symptom_names]
                results = api("post", "/engine/differential-diagnosis",
                              json={"symptom_ids": symptom_ids})

            if not results:
                st.info("No matching diseases found for this symptom combination.")
            else:
                results_df = pd.DataFrame(results)
                st.success(f"Generated {len(results_df)} potential diagnoses.")

                display_df = results_df[[
                    "disease_name", "icd11_code", "match_percentage",
                    "prior_probability", "posterior_probability_pct",
                ]].rename(columns={
                    "disease_name":            "Disease",
                    "icd11_code":              "ICD-11 Code",
                    "match_percentage":        "Symptom Match (%)",
                    "prior_probability":       "Prevalence",
                    "posterior_probability_pct": "Posterior Probability (%)",
                })

                st.dataframe(
                    display_df,
                    column_config={
                        "Disease": st.column_config.TextColumn("Disease", width="large"),
                        "ICD-11 Code": st.column_config.TextColumn("ICD-11", width="small"),
                        "Symptom Match (%)": st.column_config.ProgressColumn(
                            "Symptom Match",
                            help="Percentage of selected symptoms matching this disease",
                            format="%f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "Prevalence": st.column_config.NumberColumn(
                            "Prevalence Ratio",
                            help="Baseline Probability in Population",
                            format="%.4f",
                        ),
                        "Posterior Probability (%)": st.column_config.NumberColumn(
                            "Posterior Probability",
                            help="Calculated Bayesian Probability",
                            format="%.2f%%",
                        ),
                    },
                    use_container_width=True,
                    height=500,
                    hide_index=True,
                )

                st.markdown("---")
                st.markdown("##### 🧮 How it works:")
                st.markdown("""
                - **Prior Probability**: Baseline disease prevalence in general population.
                - **Likelihood Ratio (LR+)**: Mathematical derivation from clinical finding Sensitivity / (1 - Specificity).
                - **Posterior Probability**: Final Bayesian calculation multiplying Prior ODDs by combined LR+ of selected symptoms.
                """)

# SQL QUERIES
with tab_queries:
    st.markdown("###  SQL Queries & Output")
    st.caption("MongoDB aggregation pipelines — equivalent SQL shown for each query")

    QUERIES = [
        "Q1 – Top diseases by number of associated symptoms",
        "Q2 – Symptoms with high sensitivity (>= 0.85)",
        "Q3 – Diseases sorted by prevalence rate",
        "Q4 – Associations grouped by body system",
        "Q5 – Rules with highest confidence modifier",
        "Q6 – Set Intersection: Dynamic Symptom Match",
    ]

    SQL_EQUIV = {
        "Q1 – Top diseases by number of associated symptoms": """\
SELECT d.disease_name, COUNT(*) AS symptom_count
FROM symptom_disease_associations a
JOIN diseases d ON a.disease_id = d.disease_id
GROUP BY d.disease_name
ORDER BY symptom_count DESC;""",

        "Q2 – Symptoms with high sensitivity (>= 0.85)": """\
SELECT s.symptom_name, d.disease_name, a.sensitivity, a.specificity
FROM symptom_disease_associations a
JOIN symptoms s ON a.symptom_id = s.symptom_id
JOIN diseases d ON a.disease_id = d.disease_id
WHERE a.sensitivity >= 0.85
ORDER BY a.sensitivity DESC;""",

        "Q3 – Diseases sorted by prevalence rate": """\
SELECT disease_name, icd11_code, prevalence_rate
FROM diseases
ORDER BY prevalence_rate DESC;""",

        "Q4 – Associations grouped by body system": """\
SELECT s.body_system,
       COUNT(*)                         AS association_count,
       ROUND(AVG(a.association_strength), 3) AS avg_strength
FROM symptom_disease_associations a
JOIN symptoms s ON a.symptom_id = s.symptom_id
GROUP BY s.body_system
ORDER BY association_count DESC;""",

        "Q5 – Rules with highest confidence modifier": """\
SELECT rule_name, suggested_disease_id, confidence_modifier, priority
FROM diagnosis_rules
ORDER BY confidence_modifier DESC;""",

        "Q6 – Set Intersection: Dynamic Symptom Match": """\
-- SET INTERSECTION: Find diseases associated with BOTH selected symptoms
SELECT d.disease_name
FROM symptom_disease_associations a1
JOIN symptom_disease_associations a2 ON a1.disease_id = a2.disease_id
JOIN diseases d ON a1.disease_id = d.disease_id
WHERE a1.symptom_id = '<S1>' AND a2.symptom_id = '<S2>';""",
    }

    # Map query label → API endpoint path
    QUERY_ENDPOINTS = {
        QUERIES[0]: "/queries/top-diseases-by-symptoms",
        QUERIES[1]: "/queries/high-sensitivity-symptoms",
        QUERIES[2]: "/queries/diseases-by-prevalence",
        QUERIES[3]: "/queries/associations-by-body-system",
        QUERIES[4]: "/queries/top-rules-by-confidence",
        QUERIES[5]: "/queries/symptom-set-intersection",
    }

    chosen = st.selectbox("Choose a query", QUERIES)

    col_q, col_s = st.columns([1, 1])
    with col_s:
        st.markdown("**Equivalent SQL**")
        st.code(SQL_EQUIV[chosen], language="sql")

    with col_q:
        st.markdown("**MongoDB Result**")
        
        if chosen == QUERIES[5]:
            all_symptoms = api("get", "/symptoms")
            if all_symptoms:
                sym_map = {s["symptom_name"]: s["symptom_id"] for s in all_symptoms}
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    s1_name = st.selectbox("Symptom 1", list(sym_map.keys()), index=0)
                with col_s2:
                    s2_name = st.selectbox("Symptom 2", list(sym_map.keys()), index=min(1, len(sym_map)-1))
                    
                if st.button("Run Query"):
                    s1_id = sym_map[s1_name]
                    s2_id = sym_map[s2_name]
                    rows = api("get", f"{QUERY_ENDPOINTS[chosen]}?s1={s1_id}&s2={s2_id}")
                    if rows:
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=250)
                        st.caption(f"{len(rows)} rows returned")
                    else:
                        st.info("No diseases found with BOTH symptoms.")
            else:
                st.warning("No symptoms found in DB.")
        else:
            if st.button("Run Query"):
                rows = api("get", QUERY_ENDPOINTS[chosen])
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=340)
                    st.caption(f"{len(rows)} rows returned")
                else:
                    st.info("No results.")
            else:
                st.info("Press **Run Query** to see results.")

# CRUD OPERATIONS
with tab_crud:
    st.markdown("###  CRUD Operations")
    st.caption("Create · Read · Update · Delete on symptoms and diseases")

    entity = st.radio("Select entity", [" Symptoms", " Diseases"], horizontal=True)

    st.markdown("---")

    # Symptoms CRUD
    if entity == " Symptoms":
        col_add, col_del, col_upd = st.columns(3)

        with col_add:
            st.markdown("#### Add Symptom")
            new_id   = st.text_input("symptom_id",   placeholder="S021",           key="s_add_id")
            new_code = st.text_input("symptom_code",  placeholder="SNOMED-XXXXXXX", key="s_add_code")
            new_name = st.text_input("symptom_name",  placeholder="e.g. Sweating",  key="s_add_name")
            new_body = st.text_input("body_system",   placeholder="e.g. Systemic",  key="s_add_body")
            if st.button("Insert", key="s_insert"):
                if new_id and new_code and new_name and new_body:
                    try:
                        api("post", "/symptoms", json={
                            "symptom_id":   new_id,
                            "symptom_code": new_code,
                            "symptom_name": new_name,
                            "body_system":  new_body,
                        })
                        st.success(f"Inserted {new_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)
                else:
                    st.error("All fields are required.")

        with col_del:
            st.markdown("#### Delete Symptom")
            del_id = st.text_input("symptom_id to delete", placeholder="S021", key="s_del_id")
            if st.button("Delete", key="s_delete", type="primary"):
                if del_id:
                    try:
                        api("delete", f"/symptoms/{del_id}")
                        st.success(f"Deleted {del_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)

        with col_upd:
            st.markdown("#### Update Symptom Name")
            upd_id   = st.text_input("symptom_id to update", placeholder="S001", key="s_upd_id")
            upd_name = st.text_input("New symptom_name",     placeholder="New name", key="s_upd_name")
            if st.button("Update", key="s_update"):
                if upd_id and upd_name:
                    try:
                        api("put", f"/symptoms/{upd_id}", json={"symptom_name": upd_name})
                        st.success(f"Updated {upd_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)

        st.markdown("---")
        st.markdown("#### Current Symptoms")
        data = api("get", "/symptoms")
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=350)

    # Diseases CRUD 
    else:
        col_add, col_del, col_upd = st.columns(3)

        with col_add:
            st.markdown("#### Add Disease")
            new_id   = st.text_input("disease_id",   placeholder="D013",        key="d_add_id")
            new_code = st.text_input("icd11_code",    placeholder="e.g. 8B20",   key="d_add_code")
            new_name = st.text_input("disease_name",  placeholder="e.g. Malaria", key="d_add_name")
            new_prev = st.number_input("prevalence_rate", 0.0, 1.0, 0.01,
                                       step=0.001, format="%.3f", key="d_add_prev")
            if st.button("Insert", key="d_insert"):
                if new_id and new_code and new_name:
                    try:
                        api("post", "/diseases", json={
                            "disease_id":       new_id,
                            "icd11_code":       new_code,
                            "disease_name":     new_name,
                            "prevalence_rate":  new_prev,
                        })
                        st.success(f"Inserted {new_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)
                else:
                    st.error("All fields are required.")

        with col_del:
            st.markdown("#### Delete Disease")
            del_id = st.text_input("disease_id to delete", placeholder="D013", key="d_del_id")
            if st.button("Delete", key="d_delete", type="primary"):
                if del_id:
                    try:
                        api("delete", f"/diseases/{del_id}")
                        st.success(f"Deleted {del_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)

        with col_upd:
            st.markdown("#### Update Disease Name")
            upd_id   = st.text_input("disease_id to update", placeholder="D001", key="d_upd_id")
            upd_name = st.text_input("New disease_name",     placeholder="New name", key="d_upd_name")
            if st.button("Update", key="d_update"):
                if upd_id and upd_name:
                    try:
                        api("put", f"/diseases/{upd_id}", json={"disease_name": upd_name})
                        st.success(f"Updated {upd_id}")
                        st.rerun()
                    except requests.HTTPError as e:
                        detail = e.response.json().get("detail", str(e))
                        st.error(detail)

        st.markdown("---")
        st.markdown("#### Current Diseases")
        data = api("get", "/diseases")
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=350)
