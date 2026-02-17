import streamlit as st
from pymongo import MongoClient

@st.cache_resource
def init_connection():
    """
    Initialize MongoDB Atlas connection
    Uses st.cache_resource to maintain single connection across reruns
    """
    return MongoClient(st.secrets["MONGO_URI"])

def get_database():
    """
    Get the clinical decision support database
    Returns: MongoDB database object
    """
    client = init_connection()
    return client["clinical_decision_support"]

def get_collections():
    """
    Get all Module M7 collections
    Returns: Dictionary of collection objects
    """
    db = get_database()
    return {
        'symptoms': db.symptoms,
        'diseases': db.diseases,
        'symptom_disease_associations': db.symptom_disease_associations,
        'diagnosis_rules': db.diagnosis_rules
    }

def test_connection():
    """
    Test MongoDB Atlas connection
    Returns: True if successful, False otherwise
    """
    try:
        client = init_connection()
        client.admin.command('ping')
        return True
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return False
