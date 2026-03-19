"""
Module M7: Symptom–Disease Mapping – FastAPI Backend
Entry point: uvicorn api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import symptoms, diseases, associations, rules, engine, queries, stats

app = FastAPI(
    title="M7 – Symptom–Disease Mapping API",
    description=(
        "REST API for Module M7 of the AI-Based Clinical Decision Support System. "
        "Exposes CRUD operations, analytical queries, and a Bayesian diagnostic engine "
        "over the MongoDB symptom-disease mapping database."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Streamlit to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups
app.include_router(stats.router)
app.include_router(symptoms.router)
app.include_router(diseases.router)
app.include_router(associations.router)
app.include_router(rules.router)
app.include_router(engine.router)
app.include_router(queries.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe used by the Streamlit frontend on startup."""
    return {"status": "ok", "module": "M7 – Symptom–Disease Mapping"}
