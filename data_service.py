import json

def load_buses(filename='data/buses.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_buses(buses, filename='data/buses.json'):
    with open(filename, 'w') as f:
        json.dump(buses, f, indent=4)

def load_users(filename='data/users.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users(users, filename='data/users.json'):
    with open(filename, 'w') as f:
        json.dump(users, f, indent=4)
