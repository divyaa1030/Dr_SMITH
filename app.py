from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = "dr_smith_super_secret_key_2026"

# Upload folder for OCR
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ====================== DATABASE ======================
from database.db import patients, doctors, records

def generate_patient_id():
    return f"SMT-{random.randint(1000, 9999)}"

# ====================== ROUTES ======================

@app.route('/')
def index():
    return render_template('login.html')

# ====================== PATIENT ROUTES ======================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.form
            patient_id = generate_patient_id()

            patient_data = {
                "patient_id": patient_id,
                "name": data['name'],
                "email": data['email'],
                "password": generate_password_hash(data['password']),
                "age": int(data['age']),
                "gender": data['gender'],
                "aadhar": data['aadhar'],
                "contact": data['contact']
            }

            # Insert into MongoDB
            result = patients.insert_one(patient_data)

            if result.inserted_id:
                # Auto login after registration
                session.clear()
                session['user_id'] = str(result.inserted_id)
                session['patient_id'] = patient_id
                session['name'] = data['name']

                flash(f'Registration Successful! Welcome, {data["name"]}', 'success')
                return redirect(url_for('patient_home'))
            else:
                flash('Registration failed. Please try again.', 'danger')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print("Registration Error:", e)   # This will show in terminal

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = patients.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        session.clear()
        session['user_id'] = str(user['_id'])
        session['patient_id'] = user['patient_id']
        session['name'] = user['name']
        flash('Login Successful!', 'success')
        return redirect(url_for('patient_home'))

    flash('Invalid Email or Password', 'danger')
    return redirect(url_for('index'))


# ====================== PATIENT PAGES ======================
@app.route('/patient/home')
def patient_home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('patient_home.html', 
                         name=session.get('name'), 
                         patient_id=session.get('patient_id'))


@app.route('/patient/records')
def patient_records():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_records = list(records.find({"patient_id": session['patient_id']}).sort("date", -1))
    return render_template('patient_records.html', records=user_records)


@app.route('/patient/profile')
def patient_profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = patients.find_one({"patient_id": session['patient_id']})
    return render_template('patient_profile.html', user=user)


# ====================== OCR ======================
@app.route('/ocr', methods=['GET', 'POST'])
def ocr_scan():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    extracted_text = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extracted_text = f"[OCR Result from {filename}]\n\n" \
                           "Medicine: Paracetamol 500mg\n" \
                           "Dosage: 1-0-1\n" \
                           "Doctor: Dr. Sharma\n" \
                           f"Date: {datetime.now().strftime('%Y-%m-%d')}"

            records.insert_one({
                "patient_id": session['patient_id'],
                "type": "OCR Prescription",
                "content": extracted_text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            flash('Prescription scanned successfully!', 'success')

    return render_template('ocr_scan.html', extracted_text=extracted_text)


# ====================== OTHER PATIENT FEATURES ======================
@app.route('/drug_checker')
def drug_checker():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('drug_checker.html')


@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('analytics.html')


# ====================== DOCTOR ROUTES ======================
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == "doc@gmail.com" and password == "password123":
            session.clear()
            session['doctor'] = True
            session['doctor_name'] = "Dr. Rajesh Sharma"
            flash('Welcome Doctor!', 'success')
            return redirect(url_for('doctor_dashboard'))

        flash('Invalid Doctor Credentials', 'danger')

    return render_template('doctor_login.html')


@app.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        data = request.form
        
        doctors.insert_one({
            "full_name": data['full_name'],
            "email": data['email'],
            "password": generate_password_hash(data['password']),
            "hospital": data['hospital'],
            "speciality": data['speciality'],
            "reg_no": data['reg_no'],
            "contact": data['contact'],
            "aadhar": data['aadhar'],
            "verified": False,
            "registered_on": datetime.now().strftime("%Y-%m-%d")
        })
        
        flash('Registration Successful! Your account is under review.', 'success')
        return redirect(url_for('doctor_login'))
    
    return render_template('doctor_register.html')


@app.route('/doctor/dashboard')
def doctor_dashboard():
    if not session.get('doctor'):
        return redirect(url_for('doctor_login'))
    return render_template('doctor_dashboard.html')


# ====================== LOGOUT ======================
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)