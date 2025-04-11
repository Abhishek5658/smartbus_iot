from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
DB_FILE = '/data/routes.db'


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_no TEXT NOT NULL,
        path TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS buses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_no TEXT NOT NULL,
        route_no TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS gps_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_no TEXT,
        latitude REAL,
        longitude REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bus_status (
        bus_no TEXT PRIMARY KEY,
        air_quality INTEGER,
        passenger_count INTEGER
    )''')

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/my_bus')
def my_bus():
    return render_template('my_bus.html')

@app.route('/routes_buses')
def routes_buses():
    return render_template('routes_buses.html')

@app.route('/department')
def department():
    return render_template('department.html')

# ------------------ Route API ------------------

@app.route('/add_route', methods=['POST'])
def add_route():
    data = request.get_json()
    route_no = data['route_no']
    path = data['path']
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO routes (route_no, path) VALUES (?, ?)', (route_no, path))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Route added'})

@app.route('/get_routes')
def get_routes():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM routes')
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'route_no': r[1], 'path': r[2]} for r in rows])

# ------------------ Bus API ------------------

@app.route('/add_bus', methods=['POST'])
def add_bus():
    data = request.get_json()
    bus_no = data['bus_no']
    route_no = data['route_no']
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO buses (bus_no, route_no) VALUES (?, ?)', (bus_no, route_no))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bus added'})

@app.route('/get_buses')
def get_buses():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM buses')
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'bus_no': r[1], 'route_no': r[2]} for r in rows])

@app.route('/delete_bus/<int:bus_id>', methods=['DELETE'])
def delete_bus(bus_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bus deleted'})

# ------------------ GPS & Live Data ------------------
@app.route('/update_bus_data', methods=['GET', 'POST'])
def update_bus_data():
    if request.method == 'GET':
        bus_no = request.args.get('bus_no')
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        air_quality = request.args.get('air_quality')
        passenger_count = request.args.get('passenger_count')
    else:
        data = request.get_json()
        bus_no = data.get('bus_no')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        air_quality = data.get('air_quality')
        passenger_count = data.get('passenger_count')

    if not all([bus_no, latitude, longitude]):
        return jsonify({'error': 'Missing data'}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute('INSERT INTO gps_data (bus_no, latitude, longitude) VALUES (?, ?, ?)',
                  (bus_no, latitude, longitude))

        c.execute('''
            INSERT INTO bus_status (bus_no, air_quality, passenger_count)
            VALUES (?, ?, ?)
            ON CONFLICT(bus_no) DO UPDATE SET
            air_quality = excluded.air_quality,
            passenger_count = excluded.passenger_count
        ''', (bus_no, air_quality, passenger_count))

        conn.commit()
        conn.close()
        return jsonify({'status': 'updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_bus_location/<bus_no>')
def get_bus_location(bus_no):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            SELECT latitude, longitude 
            FROM gps_data 
            WHERE bus_no = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (bus_no,))
        row = c.fetchone()
        conn.close()
        if row:
            return jsonify({'latitude': row[0], 'longitude': row[1]})
        else:
            return jsonify({'error': 'No GPS data found for this bus'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get_bus_status/<bus_no>')
def get_bus_status(bus_no):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Get latest location
        c.execute('''
            SELECT latitude, longitude 
            FROM gps_data 
            WHERE bus_no = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (bus_no,))
        gps_row = c.fetchone()

        # Get AQI + passenger count
        c.execute('SELECT air_quality, passenger_count FROM bus_status WHERE bus_no = ?', (bus_no,))
        status_row = c.fetchone()

        conn.close()

        if gps_row and status_row:
            return jsonify({
                'bus_no': bus_no,
                'latitude': gps_row[0],
                'longitude': gps_row[1],
                'air_quality': status_row[0],
                'passenger_count': status_row[1]
            })
        else:
            return jsonify({'error': 'No data found for this bus'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/init')
def manual_init():
    init_db()
    return "✅ Database initialized"



# ------------------ Init ------------------

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
