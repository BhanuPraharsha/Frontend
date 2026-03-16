"""
Module M7: Symptom–Disease Mapping Database
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
tab_home, tab_symptoms, tab_diseases, tab_assoc, tab_rules, tab_queries, tab_crud = st.tabs([
    " Home",
    " Symptoms",
    " Diseases",
    " Associations",
    " Diagnosis Rules",
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

# SQL QUERIES
with tab_queries:
    st.markdown("###  SQL Queries & Output")
    st.caption("MongoDB aggregation pipelines — equivalent SQL shown for each query")

    # shared lookup maps
    sym_map = {s["symptom_id"]: s["symptom_name"] for s in cols["symptoms"].find({}, {"_id": 0})}
    dis_map = {d["disease_id"]: d["disease_name"] for d in cols["diseases"].find({}, {"_id": 0})}

    QUERIES = [
        "Q1 – Top diseases by number of associated symptoms",
        "Q2 – Symptoms with high sensitivity (>= 0.85)",
        "Q3 – Diseases sorted by prevalence rate",
        "Q4 – Associations grouped by body system",
        "Q5 – Rules with highest confidence modifier",
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
    }

    chosen = st.selectbox("Choose a query", QUERIES)

    col_q, col_s = st.columns([1, 1])
    with col_s:
        st.markdown("**Equivalent SQL**")
        st.code(SQL_EQUIV[chosen], language="sql")

    with col_q:
        st.markdown("**MongoDB Result**")
        if st.button("Run Query"):
            if chosen == QUERIES[0]:
                pipeline = [
                    {"$group": {"_id": "$disease_id", "symptom_count": {"$sum": 1}}},
                    {"$sort": {"symptom_count": -1}},
                    {"$project": {"_id": 0,
                                  "disease_name": {"$literal": ""},   # placeholder
                                  "disease_id": "$_id",
                                  "symptom_count": 1}},
                ]
                raw = list(cols["symptom_disease_associations"].aggregate([
                    {"$group": {"_id": "$disease_id", "symptom_count": {"$sum": 1}}},
                    {"$sort": {"symptom_count": -1}},
                ]))
                rows = [{"disease_name": dis_map.get(r["_id"], r["_id"]),
                         "symptom_count": r["symptom_count"]} for r in raw]

            elif chosen == QUERIES[1]:
                raw = list(cols["symptom_disease_associations"].find(
                    {"sensitivity": {"$gte": 0.85}}, {"_id": 0}))
                rows = [{"symptom_name": sym_map.get(r["symptom_id"], r["symptom_id"]),
                         "disease_name": dis_map.get(r["disease_id"], r["disease_id"]),
                         "sensitivity":  r["sensitivity"],
                         "specificity":  r["specificity"]} for r in raw]
                rows.sort(key=lambda x: -x["sensitivity"])

            elif chosen == QUERIES[2]:
                rows = list(cols["diseases"].find(
                    {}, {"_id": 0, "disease_name": 1, "icd11_code": 1, "prevalence_rate": 1}
                ).sort("prevalence_rate", -1))

            elif chosen == QUERIES[3]:
                pipeline = [
                    {"$lookup": {"from": "symptoms", "localField": "symptom_id",
                                 "foreignField": "symptom_id", "as": "sym"}},
                    {"$unwind": "$sym"},
                    {"$group": {"_id": "$sym.body_system",
                                "association_count": {"$sum": 1},
                                "avg_strength": {"$avg": "$association_strength"}}},
                    {"$sort": {"association_count": -1}},
                    {"$project": {"_id": 0,
                                  "body_system":       "$_id",
                                  "association_count": 1,
                                  "avg_strength":      {"$round": ["$avg_strength", 3]}}},
                ]
                rows = list(cols["symptom_disease_associations"].aggregate(pipeline))

            elif chosen == QUERIES[4]:
                raw = list(cols["diagnosis_rules"].find(
                    {}, {"_id": 0}).sort("confidence_modifier", -1))
                rows = [{"rule_name":          r["rule_name"],
                         "suggested_disease":  dis_map.get(r["suggested_disease_id"], r["suggested_disease_id"]),
                         "confidence_modifier": r["confidence_modifier"],
                         "priority":           r["priority"]} for r in raw]

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
                    if cols["symptoms"].find_one({"symptom_id": new_id}):
                        st.error(f"symptom_id `{new_id}` already exists.")
                    else:
                        cols["symptoms"].insert_one({
                            "symptom_id":   new_id,
                            "symptom_code": new_code,
                            "symptom_name": new_name,
                            "body_system":  new_body,
                        })
                        st.success(f"Inserted {new_id}")
                        st.rerun()
                else:
                    st.error("All fields are required.")

        with col_del:
            st.markdown("#### Delete Symptom")
            del_id = st.text_input("symptom_id to delete", placeholder="S021", key="s_del_id")
            if st.button("Delete", key="s_delete", type="primary"):
                if del_id:
                    res = cols["symptoms"].delete_one({"symptom_id": del_id})
                    if res.deleted_count:
                        st.success(f"Deleted {del_id}")
                        st.rerun()
                    else:
                        st.error("ID not found.")

        with col_upd:
            st.markdown("#### Update Symptom Name")
            upd_id   = st.text_input("symptom_id to update", placeholder="S001", key="s_upd_id")
            upd_name = st.text_input("New symptom_name",     placeholder="New name", key="s_upd_name")
            if st.button("Update", key="s_update"):
                if upd_id and upd_name:
                    res = cols["symptoms"].update_one(
                        {"symptom_id": upd_id},
                        {"$set": {"symptom_name": upd_name}}
                    )
                    if res.matched_count:
                        st.success(f"Updated {upd_id}")
                        st.rerun()
                    else:
                        st.error("ID not found.")

        st.markdown("---")
        st.markdown("#### Current Symptoms")
        data = list(cols["symptoms"].find({}, {"_id": 0}))
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=350)

    else:  # Diseases
        col_add, col_del, col_upd = st.columns(3)

        with col_add:
            st.markdown("#### Add Disease")
            new_id   = st.text_input("disease_id",   placeholder="D013",       key="d_add_id")
            new_code = st.text_input("icd11_code",    placeholder="e.g. 8B20",  key="d_add_code")
            new_name = st.text_input("disease_name",  placeholder="e.g. Malaria", key="d_add_name")
            new_prev = st.number_input("prevalence_rate", 0.0, 1.0, 0.01,
                                       step=0.001, format="%.3f", key="d_add_prev")
            if st.button("Insert", key="d_insert"):
                if new_id and new_code and new_name:
                    if cols["diseases"].find_one({"disease_id": new_id}):
                        st.error(f"disease_id `{new_id}` already exists.")
                    else:
                        cols["diseases"].insert_one({
                            "disease_id":      new_id,
                            "icd11_code":      new_code,
                            "disease_name":    new_name,
                            "prevalence_rate": new_prev,
                        })
                        st.success(f"Inserted {new_id}")
                        st.rerun()
                else:
                    st.error("All fields are required.")

        with col_del:
            st.markdown("#### Delete Disease")
            del_id = st.text_input("disease_id to delete", placeholder="D013", key="d_del_id")
            if st.button("Delete", key="d_delete", type="primary"):
                if del_id:
                    res = cols["diseases"].delete_one({"disease_id": del_id})
                    if res.deleted_count:
                        st.success(f"Deleted {del_id}")
                        st.rerun()
                    else:
                        st.error("ID not found.")

        with col_upd:
            st.markdown("#### Update Disease Name")
            upd_id   = st.text_input("disease_id to update", placeholder="D001", key="d_upd_id")
            upd_name = st.text_input("New disease_name",     placeholder="New name", key="d_upd_name")
            if st.button("Update", key="d_update"):
                if upd_id and upd_name:
                    res = cols["diseases"].update_one(
                        {"disease_id": upd_id},
                        {"$set": {"disease_name": upd_name}}
                    )
                    if res.matched_count:
                        st.success(f"Updated {upd_id}")
                        st.rerun()
                    else:
                        st.error("ID not found.")

        st.markdown("---")
        st.markdown("#### Current Diseases")
        data = list(cols["diseases"].find({}, {"_id": 0}))
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=350)
