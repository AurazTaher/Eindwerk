from .module import Module
import gpsd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import config
import requests
import math

source = [51.009092922694535, 4.835631975611746]
destination = [50.879736634261015, 4.706302369929912]

class GPSModule(Module):
    def __init__(self,row_number,column_number,row_span,column_span):
        super().__init__(row_number,column_number,row_span,column_span)
        self.token = 'pk.eyJ1IjoicmFmYWVsYmFja3giLCJhIjoiY2xodXpxcWNpMDR3ZzNqbXc4YWJ3MjZmMSJ9.XAM9gNZEdfB26nqgx47pFw'
        gpsd.connect()
        self.previous_location = None


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
        next_step = steps[0]
        print(next_step)
        maneuver = next_step['maneuver']
        location = maneuver['location']
        bearing_after = maneuver['bearing_after']
        return location,bearing_after

    def calculate_bearing(self, point_a, point_b):
        lon_a, lat_a = point_a
        lon_b, lat_b = point_b


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
        position = self.get_lat_long()
        font = ImageFont.truetype(config.FONT_FILE, size=12)
        print(position)
        if (position is not None):
            print(position)
            next_point, bearing = self.get_next_waypoint(position, destination)
            lon,lat = next_point
            print(next_point)
            draw = ImageDraw.Draw(image)
            # Get the current lat/lon
            lat,lon = position
            current_bearing = 0    # go straight
            if (self.previous_location is not None):
                current_bearing = self.calculate_bearing(self.previous_location,[lat,lon])
            self.previous_location = [lat,lon]
            # bearing = self.calculate_bearing(source, [lat,lon])
            print(bearing)
            # drawing the first arrow
            img = Image.open(config.ARROW_FILE).convert('RGBA')
            img = img.rotate(-bearing)
            draw.bitmap((start_x,start_y),img)

            # drawing the second arrow
            img2 = Image.open(config.ARROW_FILE).convert('RGBA')
            img2 = img2.rotate(-current_bearing)
            center_x = (end_x - start_x)/2
            print(center_x)
            print(current_bearing)
            draw.bitmap((center_x,start_y),img2)

