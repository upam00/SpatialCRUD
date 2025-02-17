from flask import Flask, request, jsonify
from pymongo import MongoClient, GEOSPHERE
from bson import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['us_states_db']
states_collection = db['states']

def serialize_object_id(state):
    state['_id'] = str(state['_id'])
    return state

# Validate polygon coordinates
def validate_polygon(coordinates):
    if not isinstance(coordinates, list) or len(coordinates) != 16:
        return False
    for point in coordinates:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not isinstance(point[0], (int, float)) or not isinstance(point[1], (int, float)):
            return False
        if not (-180 <= point[0] <= 180) or not (-90 <= point[1] <= 90):
            return False
    # Check if polygon is closed (first and last points match)
    if coordinates[0] != coordinates[-1]:
        return False
    return True

# Create State 
@app.route('/states', methods=['POST'])
def create_state():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'population_density', 'coordinates']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate polygon coordinates
        if not validate_polygon(data['coordinates']):
            return jsonify({'error': 'Invalid polygon coordinates'}), 400

        state = {
            'name': data['name'],
            'population_density': float(data['population_density']),
            'boundary': {
                'type': 'Polygon',
                'coordinates': [data['coordinates']] 
            }
        }

        result = states_collection.insert_one(state)
        state['_id'] = str(result.inserted_id)
        
        return jsonify(state), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)