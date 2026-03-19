# Module M7 – Symptom–Disease Mapping Database

**Category B · IIT(ISM) DBMS Project 2025–26**

## Features
- 8-tab Streamlit dashboard: Home, Symptoms, Diseases, Associations, Diagnosis Rules, Diagnostic Engine, SQL Queries, CRUD Operations
- FastAPI REST backend exposing all data and logic as standard HTTP endpoints
- Bayesian differential diagnosis engine (sensitivity/specificity → posterior probability)
- Full CRUD for Symptoms and Diseases
- 5 analytical queries (equivalent SQL shown alongside results)
- MongoDB Atlas backend (collection: `clinical_decision_support`)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/stats` | Collection document counts |
| GET | `/symptoms` | List symptoms (optional `?body_system=`) |
| POST | `/symptoms` | Add symptom |
| PUT | `/symptoms/{id}` | Update symptom name |
| DELETE | `/symptoms/{id}` | Delete symptom |
| GET | `/diseases` | List diseases |
| POST | `/diseases` | Add disease |
| PUT | `/diseases/{id}` | Update disease name |
| DELETE | `/diseases/{id}` | Delete disease |
| GET | `/associations` | List associations (names resolved) |
| GET | `/diagnosis-rules` | List diagnosis rules |
| POST | `/engine/differential-diagnosis` | Bayesian differential diagnosis |
| GET | `/queries/top-diseases-by-symptoms` | Q1 |
| GET | `/queries/high-sensitivity-symptoms` | Q2 |
| GET | `/queries/diseases-by-prevalence` | Q3 |
| GET | `/queries/associations-by-body-system` | Q4 |
| GET | `/queries/top-rules-by-confidence` | Q5 |


## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure secrets
Your `MONGO_URI` should already be in `.streamlit/secrets.toml`:
```toml
MONGO_URI = "mongodb+srv://..."
```
The FastAPI backend reads this file automatically — no extra config needed.


### 3. Start the FastAPI backend
```bash
uvicorn api.main:app --reload
```

### 4. Start the Streamlit frontend (separate terminal)
```bash
streamlit run app.py
```

