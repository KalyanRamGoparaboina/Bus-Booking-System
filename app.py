from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ------------------ Config ------------------
UPLOAD_FOLDER = 'static/uploads/payments'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ File Paths ------------------
DATA_FOLDER = 'data'
BUSES_FILE = os.path.join(DATA_FOLDER, 'buses.json')
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

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
        try:
            data = json.load(f)
            if isinstance(data, list):
                return {user['username']: user['password'] for user in data}
            return data
        except:
            return {}

def save_users(users, filename=USERS_FILE):
    with open(filename, 'w') as f:
        json.dump(users, f, indent=4)

# ------------------ Email Function ------------------
def send_ticket_email(to_email, passenger_name, bus_name, seats, total_amount, transaction_id, source, destination, date):
    """Send ticket confirmation email (demo mode - prints to console)"""
    try:
        subject = f"VALMIKI TRAVELS - Booking Confirmation #{transaction_id}"
        print("\n" + "="*60)
        print("📧 EMAIL SENT (DEMO MODE)")
        print("="*60)
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("\nTicket Details:")
        print(f"  Passenger: {passenger_name}")
        print(f"  Bus: {bus_name}")
        print(f"  Date: {date}")
        print(f"  Route: {source} → {destination}")
        print(f"  Seats: {seats}")
        print(f"  Amount: ₹{total_amount}")
        print(f"  Transaction ID: #{transaction_id}")
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ------------------ QR Code Generator ------------------
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a237e", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

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
        except:
            last_active = datetime.utcnow()

        now = datetime.utcnow()
        if now - last_active > timedelta(minutes=15):
            session.clear()
            return redirect(url_for('login'))
        session['last_active'] = now.isoformat()

# ------------------ Routes ------------------
@app.route('/')
def home():
    website_url = request.url_root
    qr_code_data = generate_qr_code(website_url)
    return render_template('home.html', 
                         now=datetime.utcnow().date().isoformat(),
                         qr_code=qr_code_data,
                         website_url=website_url)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()
        if username in users:
            return "Username already exists.", 400
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
        return "Invalid credentials", 403
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# ------------------ Continuous Search ------------------
@app.route('/search', methods=['POST'])
def search():
    source = request.form.get('source')
    destination = request.form.get('destination')
    date_str = request.form.get('date')

    if not all([source, destination, date_str]):
        return jsonify({"error": "All fields are required"}), 400

    buses = load_buses()
    filtered_buses = []
    for bus in buses:
        if bus['source'].lower() == source.lower() and bus['destination'].lower() == destination.lower():
            # Virtualize for the requested date
            # We assume the passenger's search date is the departure date
            # But the 'departure' field in JSON might be an old date.
            # We take the TIME part from the original departure.
            try:
                orig_dep = datetime.fromisoformat(bus['departure'].replace('T', ' '))
                orig_arr = datetime.fromisoformat(bus['arrival'].replace('T', ' '))
                req_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Create virtual departure and arrival for this date
                virtual_dep = datetime.combine(req_date.date(), orig_dep.time())
                duration = orig_arr - orig_dep
                virtual_arr = virtual_dep + duration
                
                # Clone for view
                v_bus = bus.copy()
                v_bus['departure'] = virtual_dep.strftime("%Y-%m-%d %H:%M")
                v_bus['arrival'] = virtual_arr.strftime("%Y-%m-%d %H:%M")
                v_bus['duration'] = duration.seconds // 3600
                v_bus['search_date'] = date_str
                filtered_buses.append(v_bus)
            except Exception as e:
                print(f"Error parsing date for bus {bus['id']}: {e}")

    session['source'] = source
    session['destination'] = destination
    session['search_date'] = date_str

    return render_template('search_results.html', buses=filtered_buses,
                           source=source, destination=destination, date=date_str)

# ------------------ Seat Selection ------------------
@app.route('/seat_selection/<int:bus_id>')
def seat_selection(bus_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    date_str = request.args.get('date') or session.get('search_date')
    if not date_str:
        return redirect(url_for('home'))

    buses = load_buses()
    bus = next((b for b in buses if b['id'] == bus_id), None)
    if not bus:
        return redirect(url_for('home'))

    # Get booked seats for this specific date
    date_bookings = bus.get('date_bookings', {})
    booked_seats = date_bookings.get(date_str, [])

    seat_labels = []
    total_seats = bus['available_seats']
    for i in range(total_seats):
        row = i // 4 + 1
        col = chr(65 + (i % 4))
        seat_labels.append(f"{row}{col}")

    return render_template('seat_selection.html', bus=bus, booked_seats=booked_seats,
                           source=bus['source'], destination=bus['destination'],
                           seat_labels=seat_labels, search_date=date_str)

@app.route('/seat_selection/<int:bus_id>', methods=['POST'])
def seat_selection_post(bus_id):
    selected_seats_str = request.form.get('selected_seats')
    if not selected_seats_str:
        return "Select at least one seat", 400
    
    selected_seats = [s.strip() for s in selected_seats_str.split(',') if s.strip()]
    session['bus_id'] = bus_id
    session['selected_seats'] = selected_seats
    session['pickup_location'] = request.form.get('pickup_location')
    session['drop_location'] = request.form.get('drop_location')
    
    buses = load_buses()
    bus = next((b for b in buses if b['id'] == bus_id), None)
    session['total_price'] = bus['price'] * len(selected_seats)
    
    return redirect(url_for('passenger_info'))

# ------------------ Passenger Info ------------------
@app.route('/passenger_info', methods=['GET', 'POST'])
def passenger_info():
    if request.method == 'POST':
        session['passenger_name'] = request.form.get('name')
        session['passenger_phone_number'] = request.form.get('phone_number')
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
        file = request.files.get('payment_screenshot')
        
        if not transaction_id:
            return "Transaction ID is required", 400
        
        screenshot_filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            screenshot_filename = filename

        session['transaction_id'] = transaction_id
        session['payment_screenshot'] = screenshot_filename
        return redirect(url_for('booking_confirmation'))

    return render_template('payment.html',
                           total_amount=session.get('total_price', 0),
                           pickup_location=session.get('pickup_location', ''),
                           drop_location=session.get('drop_location', ''),
                           selected_seats=session.get('selected_seats', []))

@app.route('/booking_confirmation')
def booking_confirmation():
    bus_id = session.get('bus_id')
    selected_seats = session.get('selected_seats', [])
    date_str = session.get('search_date')
    
    if not all([bus_id, selected_seats, date_str]):
        return redirect(url_for('home'))

    booking_data = {
        'id': datetime.now().timestamp(),
        'user': session.get('username'),
        'passenger_name': session.get('passenger_name'),
        'email': session.get('passenger_email'),
        'phone': session.get('passenger_phone_number'),
        'seats': selected_seats,
        'amount': session.get('total_price'),
        'transaction_id': session.get('transaction_id'),
        'screenshot': session.get('payment_screenshot'),
        'date': date_str,
        'timestamp': datetime.now().isoformat()
    }

    buses = load_buses()
    bus_found = None
    for bus in buses:
        if bus['id'] == bus_id:
            if 'date_bookings' not in bus: bus['date_bookings'] = {}
            if date_str not in bus['date_bookings']: bus['date_bookings'][date_str] = []
            
            # Save seat numbers for fast lookup
            bus['date_bookings'][date_str].extend(selected_seats)
            
            # Save full details for admin
            if 'detailed_bookings' not in bus: bus['detailed_bookings'] = {}
            if date_str not in bus['detailed_bookings']: bus['detailed_bookings'][date_str] = {}
            for seat in selected_seats:
                bus['detailed_bookings'][date_str][seat] = booking_data
            
            bus_found = bus
            break
    
    save_buses(buses)
    
    # Add bus info for display in confirmation page
    booking_data['bus_name'] = bus_found['name']
    booking_data['route'] = f"{bus_found['source']} → {bus_found['destination']}"
    
    send_ticket_email(
        booking_data['email'], booking_data['passenger_name'], 
        bus_found['name'], ', '.join(selected_seats),
        booking_data['amount'], booking_data['transaction_id'],
        bus_found['source'], bus_found['destination'], date_str
    )

    return render_template('booking_confirmation.html', **booking_data)

# ------------------ My Bookings ------------------
@app.route('/my_bookings')
def my_bookings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    current_user = session['username']
    buses = load_buses()
    user_bookings = []
    
    for bus in buses:
        detailed = bus.get('detailed_bookings', {})
        for date, seats_data in detailed.items():
            # Collecting unique bookings (one entry per transaction)
            seen_ids = set()
            for seat, info in seats_data.items():
                if info.get('user') == current_user and info.get('id') not in seen_ids:
                    info['bus_name'] = bus['name']
                    info['route'] = f"{bus['source']} → {bus['destination']}"
                    user_bookings.append(info)
                    seen_ids.add(info.get('id'))
    
    return render_template('my_bookings.html', bookings=user_bookings)

# ------------------ Admin Dashboard ------------------
@app.route('/admin')
def admin_dashboard():
    buses = load_buses()
    # Basic summary
    total_revenue = 0
    total_seats_booked = 0
    for bus in buses:
        bus_booked_count = 0
        for date, seats in bus.get('date_bookings', {}).items():
            count = len(seats)
            total_seats_booked += count
            bus_booked_count += count
        bus['total_bookings'] = bus_booked_count
        
        for date, details in bus.get('detailed_bookings', {}).items():
            unique_tx = {}
            for seat, info in details.items():
                unique_tx[info['transaction_id']] = info['amount']
            total_revenue += sum(unique_tx.values())
            
    return render_template('admin_dashboard.html', buses=buses, 
                           total_revenue=total_revenue, 
                           total_seats=total_seats_booked)

@app.route('/admin/list_buses')
def list_buses_redirect():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/bus_details/<int:bus_id>')
def admin_bus_details(bus_id):
    buses = load_buses()
    bus = next((b for b in buses if b['id'] == bus_id), None)
    if not bus: return "Bus not found", 404
    
    # Smart date selection
    # 1. Check if date is in query args
    # 2. If not, check if there are any bookings at all
    # 3. Default to today
    
    booked_dates = sorted(bus.get('date_bookings', {}).keys())
    today = datetime.utcnow().date().isoformat()
    
    requested_date = request.args.get('date')
    if requested_date:
        date_str = requested_date
    elif today in booked_dates:
        date_str = today
    elif booked_dates:
        # Show the earliest date that has bookings
        date_str = booked_dates[0]
    else:
        date_str = today

    date_bookings = bus.get('date_bookings', {}).get(date_str, [])
    detailed = bus.get('detailed_bookings', {}).get(date_str, {})
    
    seat_labels = []
    total_seats_val = bus['available_seats']
    for i in range(total_seats_val):
        row = i // 4 + 1
        col = chr(65 + (i % 4))
        seat_labels.append(f"{row}{col}")
        
    # Calculate revenue for THIS bus on THIS date
    unique_tx = {}
    for seat, info in detailed.items():
        unique_tx[info['transaction_id']] = info['amount']
    day_revenue = sum(unique_tx.values())
    
    return render_template('admin_bus_details.html', bus=bus, date=date_str, 
                           booked_seats=date_bookings, detailed=detailed,
                           seat_labels=seat_labels, day_revenue=day_revenue,
                           booked_dates=booked_dates)

@app.route('/admin/cancel_seat/<int:bus_id>/<string:date>/<string:seat_label>', methods=['POST'])
def cancel_seat(bus_id, date, seat_label):
    buses = load_buses()
    for bus in buses:
        if bus['id'] == bus_id:
            # 1. Remove from simple lookup
            if date in bus.get('date_bookings', {}):
                if seat_label in bus['date_bookings'][date]:
                    bus['date_bookings'][date].remove(seat_label)
            
            # 2. Remove from detailed info
            if date in bus.get('detailed_bookings', {}):
                if seat_label in bus['detailed_bookings'][date]:
                    del bus['detailed_bookings'][date][seat_label]
            
            save_buses(buses)
            break
            
    return redirect(url_for('admin_bus_details', bus_id=bus_id, date=date))

@app.route('/admin/add_bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        buses = load_buses()
        new_id = max([b['id'] for b in buses], default=0) + 1
        new_bus = {
            'id': new_id,
            'name': request.form.get('name'),
            'departure': request.form.get('departure'),
            'arrival': request.form.get('arrival'),
            'source': request.form.get('source'),
            'destination': request.form.get('destination'),
            'price': float(request.form.get('price')),
            'available_seats': int(request.form.get('available_seats')),
            'date_bookings': {},
            'detailed_bookings': {}
        }
        buses.append(new_bus)
        save_buses(buses)
        return redirect(url_for('admin_dashboard'))
    return render_template('add_bus.html')

@app.route('/admin/delete_bus/<int:bus_id>', methods=['POST'])
def delete_bus(bus_id):
    buses = load_buses()
    buses = [b for b in buses if b['id'] != bus_id]
    save_buses(buses)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
