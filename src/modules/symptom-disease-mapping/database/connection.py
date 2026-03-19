"""
MongoDB connection utilities
"""

import os
import pathlib
from functools import lru_cache
from pymongo import MongoClient


def _read_mongo_uri() -> str:
    """
    Resolve MONGO_URI from the environment
    """
    uri = os.environ.get("MONGO_URI")
    if uri:
        return uri

    module_root = pathlib.Path(__file__).resolve().parent.parent
    secrets_path = module_root / ".streamlit" / "secrets.toml"

    if secrets_path.exists():
        try:
            try:
                import tomllib
                with open(secrets_path, "rb") as f:
                    secrets = tomllib.load(f)
            except ImportError:
                import toml
                secrets = toml.load(str(secrets_path))

            uri = secrets.get("MONGO_URI")
            if uri:
                return uri
        except Exception as exc:
            raise RuntimeError(
                f"Found {secrets_path} but could not parse it: {exc}"
            ) from exc

    raise RuntimeError(
        "MONGO_URI not found."
    )


@lru_cache(maxsize=1)
def _init_connection() -> MongoClient:
    """Create a single MongoClient for the process lifetime."""
    return MongoClient(_read_mongo_uri())


def get_database():
    """Return the clinical_decision_support database."""
    return _init_connection()["clinical_decision_support"]


def get_collections() -> dict:
    """Return a dict of all four M7 collection objects."""
    db = get_database()
    return {
        "symptoms":                     db.symptoms,
        "diseases":                     db.diseases,
        "symptom_disease_associations": db.symptom_disease_associations,
        "diagnosis_rules":              db.diagnosis_rules,
    }


def test_connection() -> bool:
    """Ping MongoDB; return True on success, False on failure."""
    try:
        _init_connection().admin.command("ping")
        return True
    except Exception:
        return False
