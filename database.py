# database.py

import sqlite3

DATABASE_FILE = "appointment_system.db"

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create the 'doctors' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            max_patients INTEGER NOT NULL,
            practice_location TEXT NOT NULL,
            practice_time TEXT NOT NULL
        )
    """)
    
    # Create the 'patients' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            patient_name TEXT NOT NULL,
            patient_age INTEGER NOT NULL,  -- Assuming patient age is an integer
            gender TEXT NOT NULL
        )
    """)
    
    # Create the 'appointments' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            doctor_id INTEGER,
            patient_name TEXT NOT NULL,
            patient_age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
        )
    """)


def create_doctor(doctor_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO doctors (name, specialty, max_patients, practice_location, practice_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        doctor_data["name"],
        doctor_data["specialty"],
        doctor_data["max_patients"],
        doctor_data["practice_location"],
        doctor_data["practice_time"]
    ))
    doctor_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doctor_id

def get_doctors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors")
    doctors_data = cursor.fetchall()
    doctors = []
    for row in doctors_data:
        doctor = {
            "id": row[0],
            "name": row[1],
            "specialty": row[2],
            "max_patients": row[3],
            "practice_location": row[4],
            "practice_time": row[5],
        }
        doctors.append(doctor)
    conn.close()
    return doctors

def get_doctor_by_id(doctor_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,))
    doctor_data = cursor.fetchone()
    if doctor_data:
        doctor = {
            "id": doctor_data[0],
            "name": doctor_data[1],
            "specialty": doctor_data[2],
            "max_patients": doctor_data[3],
            "practice_location": doctor_data[4],
            "practice_time": doctor_data[5],
        }
        conn.close()
        return doctor
    else:
        conn.close()
        return None

def create_appointment(doctor_id, appointment):
    conn = get_db()
    cursor = conn.cursor()
    
    # Insert the appointment into the 'appointments' table
    cursor.execute("""
        INSERT INTO appointments (doctor_id, patient_name, patient_age, gender, appointment_date)
        VALUES (?, ?, ?, ?, ?)
    """, (doctor_id, appointment.patient_name, appointment.patient_age, appointment.gender, appointment.appointment_date))
    
    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return appointment_id


def create_patient(patient_data):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (patient_name, patient_age, gender)
        VALUES (?, ?, ?)
    """, (
        patient_data["patient_name"],
        patient_data["patient_age"],
        patient_data["gender"]
    ))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

