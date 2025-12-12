from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ------------------ File Paths ------------------
DATA_FOLDER = 'data'
BUSES_FILE = os.path.join(DATA_FOLDER, 'buses.json')
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')

# ------------------ Data Load/Save ------------------
def load_buses(filename=BUSES_FILE):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def save_buses(buses, filename=BUSES_FILE):
    with open(filename, 'w') as f:
        json.dump(buses, f, indent=4)

def load_users(filename=USERS_FILE):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            return {user['username']: user['password'] for user in data}
        return data

def save_users(users, filename=USERS_FILE):
    with open(filename, 'w') as f:
        json.dump(users, f, indent=4)

# ------------------ Auto Logout ------------------
@app.before_request
def auto_logout():
    if 'username' in session:
        last_active_str = session.get('last_active')

        try:
            if isinstance(last_active_str, str):
                last_active = datetime.fromisoformat(last_active_str)
            else:
                last_active = datetime.utcnow()
        except Exception:
            last_active = datetime.utcnow()

        now = datetime.utcnow()
        if now - last_active > timedelta(minutes=5):
            session.clear()
            return redirect(url_for('login'))

        session['last_active'] = now.isoformat()

# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users:
            return "Username already exists. Please choose a different username.", 400

        users[username] = generate_password_hash(password)
        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            session['last_active'] = datetime.utcnow().isoformat()
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 403

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# ------------------ Search Buses ------------------
@app.route('/search', methods=['POST'])
def search():
    source = request.form.get('source')
    destination = request.form.get('destination')
    date_str = request.form.get('date')

    if not source or not destination or not date_str:
        return jsonify({"error": "All fields are required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    buses = load_buses()
    filtered_buses = []
    for bus in buses:
        dep_str = bus['departure'].replace("T", " ")
        dep_time = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
        if (bus['source'].lower() == source.lower() and
            bus['destination'].lower() == destination.lower() and
            dep_time.date() == date.date()):
            arr_str = bus['arrival'].replace("T", " ")
            arr_time = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
            bus['duration'] = (arr_time - dep_time).seconds // 3600
            filtered_buses.append(bus)

    return render_template('search_results.html', buses=filtered_buses,
                           source=source, destination=destination, date=date_str)

# ------------------ Seat Selection ------------------
@app.route('/seat_selection/<int:bus_id>', methods=['GET', 'POST'])
def seat_selection(bus_id):
    buses = load_buses()
    bus = next((b for b in buses if b['id'] == bus_id), None)
    if not bus:
        return redirect(url_for('home'))

    booked_seats = bus.get('booked_seats', [])

    seat_labels = []
    total_seats = bus['available_seats']
    for i in range(total_seats):
        row = i // 4 + 1
        col = chr(65 + (i % 4))
        seat_labels.append(f"{row}{col}")

    if request.method == 'POST':
        selected_seats = request.form.getlist('selected_seats')
        pickup_location = request.form.get('pickup_location')
        drop_location = request.form.get('drop_location')

        if not selected_seats:
            return "Select at least one seat", 400

        session['selected_seats'] = selected_seats
        session['pickup_location'] = pickup_location
        session['drop_location'] = drop_location
        session['total_price'] = bus['price'] * len(selected_seats)

        return redirect(url_for('passenger_info'))

    return render_template(
        'seat_selection.html',
        bus=bus,
        booked_seats=booked_seats,
        source=bus['source'],
        destination=bus['destination'],
        seat_labels=seat_labels
    )

# ------------------ Passenger Info ------------------
@app.route('/passenger_info', methods=['GET', 'POST'])
def passenger_info():
    if request.method == 'POST':
        phone = request.form.get('phone_number')
        if not phone.isdigit() or len(phone) != 10:
            return "Phone number must be exactly 10 digits", 400

        session['passenger_name'] = request.form.get('name')
        session['passenger_phone_number'] = phone
        session['passenger_email'] = request.form.get('email')
        session['passenger_age'] = request.form.get('age')
        session['passenger_gender'] = request.form.get('gender')

        return redirect(url_for('payment'))

    return render_template('passenger_info.html')

# ------------------ Payment ------------------
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        if not transaction_id or len(transaction_id.strip()) < 5:
            return "Invalid transaction ID", 400

        session['transaction_id'] = transaction_id.strip()
        return redirect(url_for('booking_confirmation'))

    total_amount = session.get('total_price', 0)
    pickup_location = session.get('pickup_location', '')
    drop_location = session.get('drop_location', '')
    selected_seats = session.get('selected_seats', [])

    return render_template('payment.html',
                           total_amount=total_amount,
                           pickup_location=pickup_location,
                           drop_location=drop_location,
                           selected_seats=selected_seats)

# ------------------ Booking Confirmation ------------------
@app.route('/booking_confirmation')
def booking_confirmation():
    transaction_id = session.get('transaction_id', 'N/A')
    selected_seats = session.get('selected_seats', [])
    total_amount = session.get('total_price', 0)
    passenger_name = session.get('passenger_name', 'N/A')
    passenger_phone_number = session.get('passenger_phone_number', 'N/A')
    passenger_email = session.get('passenger_email', 'N/A')

    return render_template('booking_confirmation.html',
                           transaction_id=transaction_id,
                           selected_seats=selected_seats,
                           total_amount=total_amount,
                           name=passenger_name,
                           email=passenger_email,
                           phone_number=passenger_phone_number)

# ------------------ Admin Functions ------------------
@app.route('/admin/add_bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        name = request.form.get('name')
        departure = request.form.get('departure')
        arrival = request.form.get('arrival')
        source = request.form.get('source')
        destination = request.form.get('destination')
        price = request.form.get('price')
        available_seats = request.form.get('available_seats')

        if not all([name, departure, arrival, source, destination, price, available_seats]):
            return "All fields are required", 400

        buses = load_buses()
        new_bus = {
            'id': len(buses) + 1,
            'name': name,
            'departure': departure,
            'arrival': arrival,
            'source': source,
            'destination': destination,
            'price': float(price),
            'available_seats': int(available_seats),
            'booked_seats': []
        }
        buses.append(new_bus)
        save_buses(buses)

        return redirect(url_for('list_buses'))

    return render_template('add_bus.html')

@app.route('/admin/list_buses')
def list_buses():
    buses = load_buses()
    return render_template('list_buses.html', buses=buses)

@app.route('/admin/delete_bus/<int:bus_id>', methods=['POST'])
def delete_bus(bus_id):
    buses = load_buses()
    buses = [bus for bus in buses if bus['id'] != bus_id]
    save_buses(buses)
    return redirect(url_for('list_buses'))

# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)
