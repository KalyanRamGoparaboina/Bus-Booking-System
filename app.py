from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Define file paths
DATA_FOLDER = 'data'
BUSES_FILE = os.path.join(DATA_FOLDER, 'buses.json')
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')

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
        return json.load(f)

def save_users(users, filename=USERS_FILE):
    with open(filename, 'w') as f:
        json.dump(users, f, indent=4)

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
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 403

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

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
    filtered_buses = [
        bus for bus in buses
        if bus['source'].lower() == source.lower()
        and bus['destination'].lower() == destination.lower()
        and datetime.strptime(bus['departure'], "%Y-%m-%d %H:%M").date() == date.date()
    ]

    for bus in filtered_buses:
        departure_time = datetime.strptime(bus['departure'], "%Y-%m-%d %H:%M")
        arrival_time = datetime.strptime(bus['arrival'], "%Y-%m-%d %H:%M")
        duration = (arrival_time - departure_time).seconds // 3600
        bus['duration'] = duration

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "redirect": url_for('search_results', source=source, destination=destination, date=date_str)
        })
    
    return render_template('search_results.html', buses=filtered_buses, source=source, destination=destination, date=date_str)

@app.route('/search_results')
def search_results():
    source = request.args.get('source')
    destination = request.args.get('destination')
    date_str = request.args.get('date')

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format", 400

    buses = load_buses()
    filtered_buses = [
        bus for bus in buses
        if bus['source'].lower() == source.lower()
        and bus['destination'].lower() == destination.lower()
        and datetime.strptime(bus['departure'], "%Y-%m-%d %H:%M").date() == date.date()
    ]
    
    for bus in filtered_buses:
        departure_time = datetime.strptime(bus['departure'], "%Y-%m-%d %H:%M")
        arrival_time = datetime.strptime(bus['arrival'], "%Y-%m-%d %H:%M")
        duration = (arrival_time - departure_time).seconds // 3600
        bus['duration'] = duration

    return render_template('search_results.html', buses=filtered_buses, source=source, destination=destination, date=date_str)

@app.route('/seat_selection/<int:bus_id>', methods=['GET', 'POST'])
def seat_selection(bus_id):
    bus = next((b for b in load_buses() if b['id'] == bus_id), None)
    if not bus:
        return redirect(url_for('search'))
    
    if request.method == 'POST':
        selected_seats = request.form.getlist('selected_seats')
        pickup_location = request.form.get('pickup_location')
        drop_location = request.form.get('drop_location')
        total_price = request.form.get('total_amount')
        
        # Store the details in the session
        session['selected_seats'] = selected_seats
        session['pickup_location'] = pickup_location
        session['drop_location'] = drop_location
        session['total_price'] = total_price
        
        return redirect(url_for('passenger_info'))
    
    return render_template('seat_selection.html', bus=bus)

@app.route('/passenger_info', methods=['GET', 'POST'])
def passenger_info():
    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')

        # Store passenger details in the session
        session['passenger_name'] = name
        session['passenger_phone_number'] = phone_number
        session['passenger_email'] = email
        session['passenger_age'] = age
        session['passenger_gender'] = gender

        return redirect(url_for('payment'))

    return render_template('passenger_info.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')  # Get transaction ID from form
        session['transaction_id'] = transaction_id
        return redirect(url_for('booking_confirmation'))

    total_amount = session.get('total_price', 0)
    pickup_location = session.get('pickup_location', 'N/A')
    drop_location = session.get('drop_location', 'N/A')
    selected_seats = session.get('selected_seats', [])

    return render_template('payment.html',
                           total_amount=total_amount,
                           pickup_location=pickup_location,
                           drop_location=drop_location,
                           selected_seats=selected_seats)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    total_amount = request.form.get('total_amount')
    pickup_location = request.form.get('pickup_location')
    drop_location = request.form.get('drop_location')
    selected_seats = request.form.getlist('selected_seats')

    # You can add payment processing logic here

    # For now, just redirect to the booking confirmation page
    return redirect(url_for('booking_confirmation'))

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

@app.route('/admin/add_bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        # Get data from the form
        name = request.form.get('name')
        departure = request.form.get('departure')
        arrival = request.form.get('arrival')
        source = request.form.get('source')
        destination = request.form.get('destination')
        price = request.form.get('price')
        available_seats = request.form.get('available_seats')

        # Validate input
        if not all([name, departure, arrival, source, destination, price, available_seats]):
            return "All fields are required", 400
        
        # Load existing buses
        buses = load_buses()
        
        # Create new bus entry
        new_bus = {
            'id': len(buses) + 1,
            'name': name,
            'departure': departure,
            'arrival': arrival,
            'source': source,
            'destination': destination,
            'price': float(price),
            'available_seats': int(available_seats)
        }
        
        # Add to the list and save
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

if __name__ == '__main__':
    app.run(debug=True)
