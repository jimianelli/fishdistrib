"""
Fisheries Catch Distribution Website
Main Flask application for retrieving fisheries data by geographic location
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
DATABASE = 'fisheries.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create catches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT NOT NULL,
            common_name TEXT,
            catch_weight REAL NOT NULL,
            catch_year INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            region TEXT,
            vessel_type TEXT,
            fishing_method TEXT
        )
    ''')
    
    # Create biological attributes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS biological_attributes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT NOT NULL,
            common_name TEXT,
            max_length REAL,
            max_weight REAL,
            trophic_level REAL,
            habitat TEXT,
            depth_range TEXT,
            temperature_range TEXT
        )
    ''')
    
    # Insert sample data for catches
    cursor.execute('SELECT COUNT(*) FROM catches')
    if cursor.fetchone()[0] == 0:
        sample_catches = [
            ('Gadus morhua', 'Atlantic Cod', 1500.5, 2020, 58.5, -5.2, 'North Atlantic', 'Trawler', 'Bottom Trawl'),
            ('Thunnus albacares', 'Yellowfin Tuna', 850.3, 2021, 25.3, -80.1, 'Gulf of Mexico', 'Longliner', 'Longline'),
            ('Clupea harengus', 'Atlantic Herring', 2200.7, 2020, 60.1, 5.3, 'North Sea', 'Purse Seiner', 'Purse Seine'),
            ('Salmo salar', 'Atlantic Salmon', 650.2, 2021, 62.5, -6.8, 'Norwegian Sea', 'Farm', 'Aquaculture'),
            ('Gadus morhua', 'Atlantic Cod', 1320.8, 2021, 59.2, -4.8, 'North Atlantic', 'Trawler', 'Bottom Trawl'),
            ('Melanogrammus aeglefinus', 'Haddock', 980.4, 2020, 57.8, -3.5, 'North Sea', 'Trawler', 'Bottom Trawl'),
            ('Pleuronectes platessa', 'Plaice', 720.6, 2021, 54.2, 2.1, 'North Sea', 'Trawler', 'Bottom Trawl'),
            ('Merluccius merluccius', 'European Hake', 1100.9, 2020, 48.5, -9.3, 'Bay of Biscay', 'Trawler', 'Bottom Trawl'),
        ]
        cursor.executemany('''
            INSERT INTO catches (species, common_name, catch_weight, catch_year, latitude, longitude, region, vessel_type, fishing_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_catches)
    
    # Insert sample data for biological attributes
    cursor.execute('SELECT COUNT(*) FROM biological_attributes')
    if cursor.fetchone()[0] == 0:
        sample_attributes = [
            ('Gadus morhua', 'Atlantic Cod', 200.0, 96.0, 4.4, 'Demersal', '0-600m', '0-20°C'),
            ('Thunnus albacares', 'Yellowfin Tuna', 239.0, 200.0, 4.3, 'Pelagic', '0-250m', '18-31°C'),
            ('Clupea harengus', 'Atlantic Herring', 45.0, 1.0, 3.3, 'Pelagic', '0-200m', '4-15°C'),
            ('Salmo salar', 'Atlantic Salmon', 150.0, 46.0, 4.2, 'Anadromous', '0-210m', '8-14°C'),
            ('Melanogrammus aeglefinus', 'Haddock', 112.0, 17.0, 4.2, 'Demersal', '40-300m', '4-10°C'),
            ('Pleuronectes platessa', 'Plaice', 100.0, 7.0, 3.3, 'Demersal', '0-200m', '0-15°C'),
            ('Merluccius merluccius', 'European Hake', 140.0, 15.0, 4.1, 'Demersal', '30-1000m', '8-14°C'),
        ]
        cursor.executemany('''
            INSERT INTO biological_attributes (species, common_name, max_length, max_weight, trophic_level, habitat, depth_range, temperature_range)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_attributes)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_catches():
    """Search for catches by geographic location and filters"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', 100, type=float)  # km
    species = request.args.get('species', '')
    year = request.args.get('year', type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT c.*, b.max_length, b.max_weight, b.trophic_level, b.habitat, b.depth_range, b.temperature_range
        FROM catches c
        LEFT JOIN biological_attributes b ON c.species = b.species
        WHERE 1=1
    '''
    params = []
    
    # Geographic filter (simplified - using bounding box approximation)
    if lat is not None and lon is not None:
        # Approximate 1 degree = 111 km
        lat_offset = radius / 111.0
        lon_offset = radius / (111.0 * abs(cos(lat * 3.14159 / 180.0))) if lat != 0 else radius / 111.0
        query += ' AND c.latitude BETWEEN ? AND ? AND c.longitude BETWEEN ? AND ?'
        params.extend([lat - lat_offset, lat + lat_offset, lon - lon_offset, lon + lon_offset])
    
    if species:
        query += ' AND (c.species LIKE ? OR c.common_name LIKE ?)'
        params.extend([f'%{species}%', f'%{species}%'])
    
    if year:
        query += ' AND c.catch_year = ?'
        params.append(year)
    
    query += ' ORDER BY c.catch_year DESC, c.catch_weight DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        results.append({
            'id': row['id'],
            'species': row['species'],
            'common_name': row['common_name'],
            'catch_weight': row['catch_weight'],
            'catch_year': row['catch_year'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'region': row['region'],
            'vessel_type': row['vessel_type'],
            'fishing_method': row['fishing_method'],
            'biological': {
                'max_length': row['max_length'],
                'max_weight': row['max_weight'],
                'trophic_level': row['trophic_level'],
                'habitat': row['habitat'],
                'depth_range': row['depth_range'],
                'temperature_range': row['temperature_range']
            }
        })
    
    conn.close()
    return jsonify(results)

def cos(x):
    """Simple cosine implementation"""
    import math
    return math.cos(x)

@app.route('/api/species', methods=['GET'])
def get_species():
    """Get list of all species"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT species, common_name FROM catches ORDER BY common_name')
    rows = cursor.fetchall()
    
    species = [{'species': row['species'], 'common_name': row['common_name']} for row in rows]
    conn.close()
    return jsonify(species)

@app.route('/api/years', methods=['GET'])
def get_years():
    """Get list of all years with data"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT catch_year FROM catches ORDER BY catch_year DESC')
    rows = cursor.fetchall()
    
    years = [row['catch_year'] for row in rows]
    conn.close()
    return jsonify(years)

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get list of all regions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT region FROM catches WHERE region IS NOT NULL ORDER BY region')
    rows = cursor.fetchall()
    
    regions = [row['region'] for row in rows]
    conn.close()
    return jsonify(regions)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total_catches, SUM(catch_weight) as total_weight FROM catches')
    stats = dict(cursor.fetchone())
    
    cursor.execute('SELECT COUNT(DISTINCT species) as total_species FROM catches')
    stats.update(dict(cursor.fetchone()))
    
    cursor.execute('SELECT COUNT(DISTINCT region) as total_regions FROM catches')
    stats.update(dict(cursor.fetchone()))
    
    conn.close()
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
