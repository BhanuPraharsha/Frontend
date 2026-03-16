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
tab_home, tab_symptoms, tab_diseases, tab_assoc, tab_rules, tab_engine = st.tabs([
    " Home",
    " Symptoms",
    " Diseases",
    " Associations",
    " Diagnosis Rules",
    " Diagnostic Engine",
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

# DIAGNOSTIC ENGINE
with tab_engine:
    st.markdown("### 🧠 Bayesian Diagnostic Engine")
    st.caption("Generate a Differential Diagnosis based on Posterior Probability.")
    
    # 1. Fetch available symptoms for multi-select
    all_symptoms = list(cols["symptoms"].find({}, {"_id": 0, "symptom_id": 1, "symptom_name": 1}))
    sym_name_to_id = {s["symptom_name"]: s["symptom_id"] for s in all_symptoms}
    
    # 2. UI for symptom selection
    selected_symptom_names = st.multiselect(
        "Select Patient Symptoms (Pattern Recognition & Combos):",
        options=list(sym_name_to_id.keys()),
        default=[]
    )
    
    # Execute Button
    if st.button("Generate Differential Diagnosis", type="primary"):
        if not selected_symptom_names:
            st.warning("Please select at least one symptom.")
        else:
            with st.spinner("Calculating Bayesian Posteriors..."):
                from engine.differential_diagnosis import get_differential_diagnosis
                
                # Convert names back to IDs
                symptom_ids = [sym_name_to_id[name] for name in selected_symptom_names]
                
                # Fetch results
                results_df = get_differential_diagnosis(symptom_ids)
                
                if results_df.empty:
                    st.info("No matching diseases found for this symptom combination.")
                else:
                    st.success(f"Generated {len(results_df)} potential diagnoses.")
                    
                    # Formatting the dataframe for display
                    display_df = results_df[[
                        "disease_name", "icd11_code", "match_percentage", 
                        "prior_probability", "posterior_probability_pct"
                    ]].rename(columns={
                        "disease_name": "Disease",
                        "icd11_code": "ICD-11 Code",
                        "match_percentage": "Symptom Match (%)",
                        "prior_probability": "Prevalence",
                        "posterior_probability_pct": "Posterior Probability (%)"
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
                                format="%.4f"
                            ),
                            "Posterior Probability (%)": st.column_config.NumberColumn(
                                "Posterior Probability",
                                help="Calculated Bayesian Probability",
                                format="%.2f%%"
                            ),
                        },
                        use_container_width=True, 
                        height=500,
                        hide_index=True
                    )
                    
                    # Explain calculations
                    st.markdown("---")
                    st.markdown("##### 🧮 How it works:")
                    st.markdown("""
                    - **Prior Probability**: Baseline disease prevalence in general population.
                    - **Likelihood Ratio (LR+)**: Mathematical derivation from clinical finding Sensitivity / (1 - Specificity).
                    - **Posterior Probability**: Final Bayesian calculation multiplying Prior ODDs by combined LR+ of selected symptoms.
                    """)
