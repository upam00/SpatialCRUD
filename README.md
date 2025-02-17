Basic CRUD APIs for handling Spatial data Stored as GeoJSON in MOngoDB, using Flask.

For events.py file, Create/Read/Update APIs for the following object has been added.

        event = {
            'location': {
                'type': 'Point',
                'coordinates': [location['longitude'], location['latitude']]
            },
            'event_name': data['event_name'],
            'artists': data['artists'],
            'date':  datetime.fromisoformat(data['date']) ,
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'price': float(data['price'])
        }
        
Additionally, API has been added to get events nearby using $near operator of MongoDB.

For polygons.py file, Create/Read/Update APIs for the following object has been added.

    state = {
            'name': data['name'],
            'population_density': float(data['population_density']),
            'boundary': {
                'type': 'Polygon',
                'coordinates': [data['coordinates']] 
            }
        }

Additionally, API has been added to check if a point is within a poygon/state using $geoIntersects operator of MongoDB.
