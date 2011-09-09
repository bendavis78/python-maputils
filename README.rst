python-maputils
===============

A compliment to pyproj, maputils is used for plotting locations on a fixed map.  In order to convert lat/lng coordinates into x/y coordinates, you need to know three things about your map:

* Projection
* Scale (meters per pixel)
* False Northing/Easting (map offset)

Ther are other ways to get this information, but they involve setting up more complex GIS systems. This library is a quick way to get a "good enough" estimation of screen coordinates for lat/lng coordinates.

This module will help you determine scale and your northing/easting values. You're on your own figuring out what projection your map is (Google is your friend). 

In order to find the other figures, you need to know at least two points that you can plot on your map.  For example, in a US map, it's pretty easy to visually find the "four corners" (where colorado, new mexico, arizona, and utah meet) and the bottom tip of Texas (south padre island).  With these two points known, the Map class can figure out the scale and your northing/easting values.

To find these values, open up interactive python and add the places to an instance of Map::

  >>> from maputils import Map
  >>> projection_config = "+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 "\
                          "+a=6370997 +b=6370997 +units=m +no_defs"
  >>> map = Map(projection_config)
  >>> map.add_place('four corners', 36.999085, -109.045218, 244, 317)
  >>> map.add_place('south padre', 25.9772, -97.159, 462, 566)
  >>> map.scale = map.find_scale()
  >>> print round(map.scale)
  5026.0
  >>> print round(map.false_easting)
  2029618.0
  >>> print round(map.false_northing)
  -747624.0

The more "known" places you add, the more accurate your final values will be. Once you have these values, can update your projection string to reflect the false easting/northing values. In this example, false easting is +x_0 and false northing is +y_0. Now that you have the correct projection config and scale, you can instantiate your map and begin plotting locations::

  >>> from maputils import Map
  >>> false_easting = 2029618.0
  >>> false_northing = -747624.0
  >>> projection_config = "+proj=laea +lat_0=45 +lon_0=-100 +x_0=%s +y_0=%s "\
                          "+a=6370997 +b=6370997 +units=m +no_defs"
  >>> map = Map(projection_config % (false_easting, false_northing), scale=5026.0)
  >>> map.add_place('Los Angeles, CA', 34.054, -118.239)
  >>> print map.places['Los Angeles, CA'].screen_coords
  (71, 355)
