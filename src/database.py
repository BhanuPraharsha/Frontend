# src/database.py
import sqlite3
import pandas as pd
import os

DB_PATH = 'hospital.db'

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Create patients table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            disease TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Check if table is empty, if so, insert some sample data
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        sample_data = [
            ("John Doe", 45, "Hypertension", "active"),
            ("Jane Smith", 32, "Asthma", "active"),
            ("Robert Johnson", 58, "Type 2 Diabetes", "active")
        ]
        c.executemany("INSERT INTO patients (name, age, disease, status) VALUES (?, ?, ?, ?)", sample_data)
        
    conn.commit()
    conn.close()

def get_all_patients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df

def add_patient(name, age, disease):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, disease) VALUES (?, ?, ?)", (name, age, disease))
    conn.commit()
    conn.close()

def update_patient(patient_id, name, age, disease, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE patients SET name = ?, age = ?, disease = ?, status = ? WHERE id = ?", 
              (name, age, disease, status, patient_id))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()
