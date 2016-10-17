#!/usr/bin/python3

import googlemaps
from datetime import datetime

_CLIENT_ID = '708240676019-7dujrv10s061374dlp4t7qhrk4bnuh9f'
_CLIENT_SECRET = '8z4g5AOCZNGICsgUHbtRJaWY'
_GOOGLEMAPS_KEY = 'AIzaSyCRVbC0gdA-ZnJGe3w2nl5yiauE0dIWuew'


gmaps = googlemaps.Client(key=_GOOGLEMAPS_KEY)
gmaps = googlemaps.Client(key=_CLIENT_ID)

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)
