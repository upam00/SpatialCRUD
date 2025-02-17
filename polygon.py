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
    if not isinstance(coordinates, list) or len(coordinates) != 8:
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

# Read State by ID
@app.route('/states/<state_id>', methods=['GET'])
def get_state(state_id):
    try:
        state = states_collection.find_one({'_id': ObjectId(state_id)})
        if not state:
            return jsonify({'error': 'State not found'}), 404
            
        return jsonify(serialize_object_id(state))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update State
@app.route('/states/<state_id>', methods=['PUT'])
def update_state(state_id):
    try:
        data = request.get_json()
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name']
            
        if 'population_density' in data:
            update_data['population_density'] = float(data['population_density'])
            
        if 'coordinates' in data:
            if not validate_polygon(data['coordinates']):
                return jsonify({'error': 'Invalid polygon coordinates'}), 400
            update_data['boundary'] = {
                'type': 'Polygon',
                'coordinates': [data['coordinates']]
            }

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        result = states_collection.update_one(
            {'_id': ObjectId(state_id)},
            {'$set': update_data}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'State not found'}), 404

        updated_state = states_collection.find_one({'_id': ObjectId(state_id)})
        return jsonify(serialize_object_id(updated_state))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route to Find States Containing Point
@app.route('/states/contains', methods=['GET'])
def find_states_containing_point():
    try:
        longitude = float(request.args.get('longitude'))
        latitude = float(request.args.get('latitude'))

        query = {
            'boundary': {
                '$geoIntersects': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    }
                }
            }
        }

        states = list(states_collection.find(query))
        return jsonify([serialize_object_id(state) for state in states])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)