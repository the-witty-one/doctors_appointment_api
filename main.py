from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from typing import List

app = FastAPI(debug=True)


# appointment day != sunday
# 01:05:2023-17:30

# Create an SQLite database and tables if they don't exist
conn = sqlite3.connect("appointment_system.db")
conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support

# Create tables if they don't exist
conn.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        max_patients INTEGER NOT NULL,
        practice_location TEXT,
        practice_time TEXT NOT NULL
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        patient_age INTEGER NOT NULL,  -- Add patient_age column
        gender TEXT NOT NULL           -- Add gender column
    )
""")

# 01:05:2023:17:30
conn.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        patient_name TEXT NOT NULL,
        patient_age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        FOREIGN KEY (doctor_id) REFERENCES doctors (id)
    )
""")

conn.close()


class Doctor(BaseModel):
    id: int
    name: str
    specialty: str
    max_patients: int
    practice_location: str
    practice_time: str

class Patient(BaseModel):
    patient_name: str
    patient_age: int
    gender: str

class Appointment(BaseModel):
    doctor_id: int
    patient_name: str
    patient_age: int
    gender: str
    appointment_date: str


def sqlite_delete_all_tables():
    conn = sqlite3.connect('appointment_system.db')
    cursor = conn.cursor()

    tables = ['doctors', 'patients', 'appointments']

    for t in tables:
        cursor.execute(f"delete from {t};")

    conn.commit()
    conn.close()



# Function to load sample data
def load_sample_data():
    
    sqlite_delete_all_tables()


    sample_doctors = [
        {
            "name": "Dr. Smith",
            "specialty": "Cardiology",
            "max_patients": 1,
            "practice_location": "NewYork",
            "practice_time": "Mon,Tue,Wed,Thu,Fri",
        },
        {
            "name": "Dr. Johnson",
            "specialty": "Dermatology",
            "max_patients": 15,
            "practice_location": "NewYork",
            "practice_time": "Mon,Tue,Wed,Thu,Fri",
        },
        {
            "name": "Dr. Jack",
            "specialty": "Ophthalmologist",
            "max_patients": 20,
            "practice_location": "NewYork",
            "practice_time": "Mon,Tue,Wed,Thu,Fri",
        },
        {
            "name": "Dr. Jack",
            "specialty": "Gastroenterologist",
            "max_patients": 12,
            "practice_location": "NewYork",
            "practice_time": "Mon,Tue,Wed,Thu,Fri",
        },
    ]

    sample_patients = [
        
    ]
    
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()
    # Insert sample doctors into the database
    for doctor_data in sample_doctors:
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
    
    conn.commit()
    conn.close()



@app.post("/doctor/", response_model=Doctor)
def create_doctor(doctor: Doctor):
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO doctors (name, specialty, max_patients, practice_location, practice_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        doctor.name,
        doctor.specialty,
        doctor.max_patients,
        doctor.practice_location,
        doctor.practice_time
    ))
    conn.commit()
    conn.close()
    return doctor

@app.get("/doctors/{doctor_id}/", response_model=Doctor)
def read_doctor(doctor_id: int):
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Doctor(id=row[0], name=row[1], specialty=row[2], max_patients=row[3], practice_location=row[4], practice_time=row[5])
    raise HTTPException(status_code=404, detail="Doctor not found")

@app.get("/doctors/", response_model=List[Doctor])
def read_doctors():
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors")
    rows = cursor.fetchall()
    conn.close()
    doctors = []
    for row in rows:
        doctors.append(Doctor(id=row[0], name=row[1], specialty=row[2], max_patients=row[3], practice_location=row[4], practice_time=row[5]))
    return doctors

@app.post("/book-appointment/", response_model=Appointment)
def book_appointment(appointment: Appointment):
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()

    # get the doctor details
    cursor.execute("SELECT * FROM doctors WHERE id=?", (appointment.doctor_id,))
    doctor = cursor.fetchone()

    try:
        date_format = "%d-%m-%Y"
        # Convert the string to a datetime object
        date_obj = datetime.strptime(appointment.appointment_date, date_format)
        # Extract the day from the datetime object
        weekday = date_obj.weekday
        if weekday == 6:
            # booking cannot be done on sunday
            return JSONResponse(content= {"message" : "doctor is not available for the selected date"}, status_code = 403)
        
        # check if it is past date
        current_datetime = datetime.now()
        if date_obj < current_datetime:
            return JSONResponse(content= {"message" : "cannot book for a past date"}, status_code = 403)


    except ValueError:
        return JSONResponse(content= {"message" : "date is in wrong format, accepted format - 'day:month:year'"}, status_code = 403)

        



    # TODO : get the day from appointment.date, if day is sunday return faild
    # do not accept the past dates

    if doctor:
        doctor_max_patients = doctor[3]
        # app date, len(get all the appointments where date = , doc = docid, ) < doctor.max_patients,
        doctor_date_appointments = cursor.execute('''
            SELECT * FROM appointments
            WHERE doctor_id = ? AND appointment_date = ?;
        ''', (appointment.doctor_id, appointment.appointment_date)).fetchall()


        if len(doctor_date_appointments) < doctor_max_patients:
            # Insert the appointment into the 'appointments' table
            cursor.execute("""
                INSERT INTO appointments (doctor_id, patient_name, patient_age, gender, appointment_date)
                VALUES (?, ?, ?, ?, ?)
            """, (appointment.doctor_id, appointment.patient_name, appointment.patient_age, appointment.gender, appointment.appointment_date))

            # Insert the patient into the 'patients' table
            cursor.execute("""
                INSERT INTO patients (patient_name, patient_age, gender)
                VALUES (?, ?, ?)
            """, (appointment.patient_name, appointment.patient_age, appointment.gender))

            conn.commit()
            conn.close()
            return JSONResponse(content= {"message" : "appointment booked successfully!!"}, status_code = 200)
        else:
            return JSONResponse(content= {"message" : "doctor is not available for the selected date"}, status_code = 403)
    else:
        conn.close()
        return JSONResponse(content= {"message" : "doctor details not found"}, status_code = 404)





# @app.post("/patients/", response_model=Patient)
# def create_patient(patient: Patient):
#     patient_data = {
#         "patient_name": patient.patient_name,
#         "patient_location": patient.patient_location,
#         "appointment_date": patient.appointment_date
#     }
#     patient_id = create_patient(patient_data)
#     return Patient(id=patient_id, **patient_data)


@app.get("/patients/", response_model=List[Patient])
def read_patients():
    conn = sqlite3.connect("appointment_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patients_data = cursor.fetchall()
    conn.close()
    patients = []
    for row in patients_data:
        patients.append(Patient(id=row[0], patient_name=row[1], patient_age=row[2], gender=row[3]))
    return patients



if __name__=="__main__":
    import uvicorn
    # Load sample data when the application starts
    load_sample_data()
    uvicorn.run(app, host="0.0.0.0", port=8000)
