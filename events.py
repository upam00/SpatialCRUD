from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['events_db']
events_collection = db['events']


# Create Event
@app.route('/events', methods=['POST'])
def create_event():
    try:
        data = request.get_json()
        
        # Validating required fields
        required_fields = ['location', 'event_name', 'artists', 'date', 
                            'start_time', 'end_time', 'price']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Formating location as GeoJSON Point
        location = data['location']
        if not all(coord in location for coord in ['longitude', 'latitude']):
            return jsonify({'error': 'Invalid location format'}), 400

        event = {
            'location': {
                'type': 'Point',
                'coordinates': [location['longitude'], location['latitude']]
            },
            'event_name': data['event_name'],
            'artists': data['artists'],
            'date': datetime.strptime(data['date'], '%Y-%m-%d').date(),
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'price': float(data['price'])
        }

        result = events_collection.insert_one(event)
        event['_id'] = str(result.inserted_id)
        
        return jsonify(event), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

   


if __name__ == '__main__':
    app.run(debug=True)