from .module import Module
import gpsd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import config
import requests
import math
from pymongo import MongoClient

# points to simulate walking (for demo)
next_points = [[50.85974676248955, 4.706331275649237], [50.85926254302513, 4.706175707528873], [50.85925238450844, 4.705333493892339],
               [50.859235453663274, 4.704609297469949], [50.858656415058185, 4.704426907259865], [50.85843292454199, 4.703531049445617],
               [50.85821281920732, 4.702994607651255]]

def get_database():
    connection_string = 'mongodb+srv://Auraz:Auraz123@devwerkstuk.pdrqk.mongodb.net/'
    client = MongoClient(connection_string)
    db = client['smartglasses']
    return db

def get_destination_location():
    db = get_database()
    query = {"type": "destination"}
    destinations = db['places'].find(query)
    if (destinations.count() > 0):
        location = destinations[0]
        return [location['latitude'], location['longitude']]

class GPSModule(Module):
    def __init__(self,row_number,column_number,row_span,column_span):
        super().__init__(row_number,column_number,row_span,column_span)
        self.token = 'pk.eyJ1IjoicmFmYWVsYmFja3giLCJhIjoiY2xodXpxcWNpMDR3ZzNqbXc4YWJ3MjZmMSJ9.XAM9gNZEdfB26nqgx47pFw'
        gpsd.connect()
        self.previous_location = None
        self.next_point = -1


    def get_directions(self ,source, destination):
        profile = 'mapbox/walking'
        points_to_visit = [source, destination]
        coordinates = [','.join([str(point[1]), str(point[0])]) for point in points_to_visit]
        coordinates = ';'.join(coordinates)
        url = 'https://api.mapbox.com/directions/v5/' + profile + '/' + coordinates + '?access_token=' + self.token + '&steps=true'
        request = requests.get(url)
        directions_json = request.json()

        # just take the first route, there might be multiple
        routes = directions_json['routes'][0]
        # a route has a list of legs, each leg is a guide from a start to destination
        # if a route has multiple destinations, then there are multiple legs
        route_legs = routes['legs'][0]
        steps = route_legs['steps']
        
        return steps

    def get_next_waypoint(self,source,destination):
        steps = self.get_directions(source,destination)
        if (len(steps) == 0): return None
        next_step = steps[1]
        maneuver = next_step['maneuver']
        print(maneuver)
        distance = next_step['distance']
        location = maneuver['location']
        # not used right now, but can be useful
        bearing_after = maneuver['bearing_after']
        return location,distance

    # https://www.movable-type.co.uk/scripts/latlong.html
    def calculate_bearing(self, point_a, point_b):
        lat_a, lon_a = point_a
        lat_b, lon_b = point_b

        y = math.sin(lon_b - lon_a) * math.cos(lat_b)
        x = (math.cos(lat_a) * math.sin(lat_b)) - (math.sin(lat_a) * math.cos(lat_b) * math.cos(lon_b - lon_a))
        theta = math.atan2(y,x)
        bearing = (theta * 180/math.pi + 360) % 360
        return bearing

    def get_lat_long(self):
        packet = gpsd.get_current()
        if packet.mode >= 2:
            latitude = packet.lat
            longitude = packet.lon
            return latitude,longitude
        return None

    def draw(self,image,start_x,start_y,end_x,end_y):
        destination = get_destination_location()
        position = self.get_lat_long()
        font = ImageFont.truetype(config.FONT_FILE, size=12)
        # this code is to simulate walking, remove if not needed
        if (self.next_point >-1):
            print("walking")
            position = next_points[self.next_point]
            print(position)
        if (position is not None):
            # keep in mind that next_point is lon/lat instead of lat/lon
            next_point, distance = self.get_next_waypoint(position, destination)
            draw = ImageDraw.Draw(image)
            # Get the current lat/lon
            current_bearing = 0    # go straight
            if (self.previous_location is not None):
                print('bearing between:')
                print(self.previous_location)
                print(position)
                current_bearing = self.calculate_bearing(self.previous_location,position)
                print('bearing:')
                print(current_bearing)
            self.previous_location = position
            
            lon,lat = next_point
            bearing = self.calculate_bearing(position, [lat,lon])
            # drawing the first arrow
            img = Image.open(config.ARROW_FILE).convert('RGBA')
            img = img.rotate(-bearing)
            draw.bitmap((start_x,start_y),img)

            # drawing the second arrow
            img2 = Image.open(config.ARROW_FILE).convert('RGBA')
            img2 = img2.rotate(-current_bearing)
            center_x = (end_x - start_x)/2
            draw.bitmap((center_x,start_y),img2)

            # writing the distance text
            n_rows = self.end_row - self.row
            y_diff = (end_y - start_y) / n_rows
            start_y = y_diff * (n_rows-1) + (y_diff/2)
            draw.text((start_x,start_y), str(distance) + " Meter", font=font, fill=0)

            # this code is to simulate walking, remove when not needed
            self.next_point += 1 #[lat,lon]

