from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'routes.db'

# 🧱 Create tables if not exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Table for routes
    c.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_no TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')

    # Table for buses
    c.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_no TEXT NOT NULL,
            route_no TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# 🔁 Initialize DB on startup
init_db()

# 🌐 Render main page
@app.route('/')
def home():
    return render_template('index.html')

# ✅ API: Add new route
@app.route('/add_route', methods=['POST'])
def add_route():
    data = request.get_json()
    route_no = data.get('route_no')
    path = data.get('path')  # path is stored as JSON string
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO routes (route_no, path) VALUES (?, ?)', (route_no, path))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Route added successfully!'})

# ✅ API: Add new bus
@app.route('/add_bus', methods=['POST'])
def add_bus():
    data = request.get_json()
    bus_no = data.get('bus_no')
    route_no = data.get('route_no')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO buses (bus_no, route_no) VALUES (?, ?)', (bus_no, route_no))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bus added successfully!'})

# ✅ API: Get all routes
@app.route('/get_routes', methods=['GET'])
def get_routes():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM routes')
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'route_no': r[1], 'path': r[2]} for r in rows])

# ✅ API: Get all buses
@app.route('/get_buses', methods=['GET'])
def get_buses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM buses')
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': b[0], 'bus_no': b[1], 'route_no': b[2]} for b in rows])

# ✅ API: Delete route
@app.route('/delete_route/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM routes WHERE id = ?', (route_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Route deleted'})

# ✅ API: Delete bus
@app.route('/delete_bus/<int:bus_id>', methods=['DELETE'])
def delete_bus(bus_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bus deleted'})

@app.route('/department')
def department_page():
    return render_template('department.html')

# ✅ API: Update route
@app.route('/update_route/<int:route_id>', methods=['POST'])
def update_route(route_id):
    data = request.get_json()
    route_no = data.get('route_no')
    path = data.get('path')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE routes SET route_no = ?, path = ? WHERE id = ?', (route_no, path, route_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Route updated successfully!'})

# ✅ API: Update bus
@app.route('/update_bus/<int:bus_id>', methods=['POST'])
def update_bus(bus_id):
    data = request.get_json()
    bus_no = data.get('bus_no')
    route_no = data.get('route_no')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE buses SET bus_no = ?, route_no = ? WHERE id = ?', (bus_no, route_no, bus_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bus updated successfully!'})

@app.route('/routes_buses')
def routes_buses_page():
    return render_template('routes_buses.html')

@app.route('/my_bus')
def my_bus_page():
    return render_template('my_bus.html')

# 🗺 Store GPS locations per bus number
bus_locations = {}  # keep this at the top globally

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    bus_no = data.get("bus_no")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not all([bus_no, latitude, longitude]):
        return jsonify({"status": "error", "message": "Missing data"}), 400

    bus_locations[bus_no] = {"latitude": latitude, "longitude": longitude}
    print(f"📡 Bus {bus_no} updated: ({latitude}, {longitude})")
    
    return jsonify({"status": "success", "message": "Location saved!"})

@app.route('/get_bus_location/<bus_no>', methods=['GET'])
def get_bus_location(bus_no):
    if bus_no in bus_locations:
        return jsonify(bus_locations[bus_no])
    else:
        return jsonify({"message": "No location found"}), 404





if __name__ == '__main__':
    app.run(debug=True)
