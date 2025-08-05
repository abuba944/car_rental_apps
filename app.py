from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from flask_mail import Mail, Message
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
app = Flask(__name__)
DB_NAME = 'cars.db'

# ========== Mail Configuration ==========
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # 👈 Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'your_app_password'     # 👈 Use Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# ========== Database Setup ==========
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                color TEXT,
                speed TEXT,
                price_per_day INTEGER,
                location TEXT,
                description TEXT,
                image_url TEXT
            )
        ''')
        
        c.execute('SELECT COUNT(*) FROM cars')
        if c.fetchone()[0] == 0:
            cars = [
                ("Toyota Camry", "Silver", "220km/h", 15000, "Lagos", "A reliable fuel-efficient car.", "/static/images/camry.png"),
                ("Honda Accord", "Black", "215km/h", 16000, "Abuja", "Comfortable and stylish sedan.", "/static/images/accord.png"),
                ("Lexus RX350", "White", "210km/h", 25000, "Kano", "Luxury SUV with powerful engine.", "/static/images/rx350.png"),
                ("Mercedes C300", "Red", "240km/h", 30000, "Port Harcourt", "Elegant and fast luxury car.", "/static/images/c300.png"),
                ("Toyota Highlander", "Blue", "200km/h", 20000, "Enugu", "Spacious for long trips.", "/static/images/highlander.png"),
                ("Sporty Car", "Green", "300km/h", 35000, "Jos", "Fast like a jet.", "/static/images/sport_car.png")
            ]
            c.executemany('''
                INSERT INTO cars (name, color, speed, price_per_day, location, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', cars)
        conn.commit()
        conn.close()

# ========== Routes ==========

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cars', methods=['POST'])
def show_cars():
    state = request.form['state']
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM cars WHERE location = ?', (state,))
    cars = c.fetchall()
    conn.close()
    return render_template('cars.html', state=state, cars=cars)

@app.route('/book_car/<int:car_id>', methods=['GET', 'POST'])
def book_car(car_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
    car = c.fetchone()
    conn.close()

    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']

        # ===== Send Email Invoice =====
        msg = Message("Car Booking Invoice", recipients=[email])
        msg.body = f"""
Hello {fullname},

Thank you for booking with Jimoh's Car Rentals!

Booking Details:
----------------------
Car: {car['name']}
Location: {car['location']}
Speed: {car['speed']}
Color: {car['color']}
Price per Day: ₦{car['price_per_day']}

Your Details:
----------------------
Name: {fullname}
Email: {email}
Phone: {phone}

We look forward to serving you.

Best Regards,  
Jimoh's Car Rentals Team
        """
        try:
            mail.send(msg)
            print("✅ Invoice sent to:", email)
        except Exception as e:
            print("❌ Email failed:", e)

        return render_template('success.html', car=car, fullname=fullname, email=email, phone=phone)

    return render_template('book.html', car=car)

@app.route('/success')
def success():
    return render_template('success.html')

# ========== Run App ==========
if __name__ == '__main__':
    init_db()
    app.run(debug=True)