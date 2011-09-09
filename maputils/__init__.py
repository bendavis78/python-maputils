from pyproj import Proj
import numpy
import math

def distance(p1,p2):
    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    return math.sqrt((dx**2) + (dy**2))

class Place(object):
    def __init__(self, map, name, lat, lng, known_x=None, known_y=None, data=None):
        self.map = map
        self.name = name
        self.data = data or {}
        self.lat = lat
        self.lng = lng
        self.known_x = known_x
        self.known_y = known_y

    @property
    def known_xy(self):
        return self.known_x, self.known_y
    
    @property
    def projected_coords(self):
        x, y = self.map.projection(self.lng, self.lat)
        return x, y
    
    @property
    def screen_coords(self):
        mx, my = self.projected_coords
        x = int(round(mx/self.map.scale))
        y = int(round(my/self.map.scale))*-1
        return x,y

    def __repr__(self):
        return '<Place: %s>' % self.name
        

class Map(object):
    scale = None
    places = []
    projection = None

    def __init__(self, *args, **kwargs):
        scale = kwargs.pop('scale', None)
        if scale:
            self.set_scale(scale)
        if args or kwargs:
            self.set_projection(*args, **kwargs)
    
    def set_scale(self, scale):
        self.scale = scale

    def set_projection(self, *args, **kwargs):
        self.projection = Proj(*args, **kwargs)

    def add_place(self, *args, **kwargs):
        self.places.append(Place(self, *args, **kwargs))
    
    def find_scale(self):
        """
        Finds the scale (zoom level) given a set of known points on the map. 
        """
        known_places = [p for p in self.places if p.known_x and p.known_y]
        if len(known_places) < 2:
            raise ValueError("Need two more place objects with known x,y coords in order to calibrate")
        # We need to know the "zoom" level for the map, so we calculate a ratio
        # from the given known points. 
        ratios = []
        self.tracked_ratios = {}
        # calculate an average ratio from a set of ratios for distances between
        # each point
        calculated = []
        for place in known_places:
            for other_place in known_places:
                if place.name == other_place.name or (place, other_place) in calculated or (other_place, place) in calculated:
                    continue
                projected_distance = distance(place.projected_coords, other_place.projected_coords)
                pixel_distance = distance(place.known_xy, other_place.known_xy)
                ratio = projected_distance/pixel_distance
                ratios.append(ratio)
                calculated.append((place, other_place))
                self.tracked_ratios['%s - %s' % (place.name, other_place.name)] = projected_distance, pixel_distance, ratio
        
        # do these look fishy?
        self.stddev = numpy.std(ratios)
        if self.stddev > 100: # FIXME: this method doesn't scale up well, since it could deviate more or less based on map scale.
            # see if we can fish out the bad ones
            raise ValueError("The known x,y values for the given places seem fishy. The distances between given coords deviate too much from their real distance for this projection. Please double check each coordinate. (STDDEV=%s)" % self.stddev)

        # average out the ratios
        return sum(ratios) / len(ratios)
    
    def auto_scale(self):
        self.scale = self.find_scale()
    
    def find_origin(self):
        """
        Finds the origin of the map based on a known point.  
        """
        known_places = [p for p in self.places if p.known_x and p.known_y]
        if len(known_places) == 0:
            raise ValueError("Need one more place objects with known x,y coords in order to find map origin")
        known_place = known_places[0]
        if not self.scale:
            raise ValueError("Scale must first be set in order to find map origin")
        if not (known_place.known_x and known_place.known_y):
            raise ValueError("Known place must have known_x/known_y values in order to find map origin")
        m = known_place.projected_coords
        p = known_place.known_xy
        origin = m[0]-(p[0]*self.scale), m[1]-(p[1]*self.scale)*-1
        return origin

    @property
    def false_northing(self):
        origin = self.find_origin()
        return origin[1] * -1
    
    @property
    def false_easting(self):
        origin = self.find_origin()
        return origin[0] * -1
