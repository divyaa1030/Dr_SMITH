from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["dr_smith"]

patients = db.patients
doctors = db.doctors
records = db.records
reminders = db.reminders