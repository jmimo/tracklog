from collections import namedtuple
from math import sin, cos, atan2, sqrt, radians, asin, degrees

Wgs84Point = namedtuple('Wgs84Point', ['latitude', 'longitude'])

EARTH_RADIUS_IN_METERS = 6371000


def distance(start, end):
    startLatitude = radians(start.latitude)
    startLongitude = radians(start.longitude)
    endLatitude = radians(end.latitude)
    endLongitude = radians(end.longitude)
    distanceLatitude = endLatitude - startLatitude
    distanceLongitude = endLongitude - startLongitude

    angle = sin(distanceLatitude / 2) * sin(distanceLatitude / 2) + \
            cos(startLatitude) * cos(endLatitude) * \
            sin(distanceLongitude / 2) * sin(distanceLongitude / 2)

    radDistance = 2 * atan2(sqrt(angle), sqrt(1 - angle))

    return EARTH_RADIUS_IN_METERS * radDistance


def bearing(start, end):
    startLatitude = radians(start.latitude)
    startLongitude = radians(start.longitude)
    endLatitude = radians(end.latitude)
    endLongitude = radians(end.longitude)

    y = sin(endLongitude - startLongitude) * cos(endLatitude)
    x = cos(startLatitude) * sin(endLatitude) - \
        sin(startLatitude) * cos(endLatitude) * \
        cos(endLongitude - startLongitude)
    return atan2(y, x)


def point(start, distance, phi):
    start_latitude = radians(start.latitude)
    start_longitude = radians(start.longitude)
    angular_distance = distance / EARTH_RADIUS_IN_METERS

    end_latitude = asin(sin(start_latitude) * cos(angular_distance) +
                       cos(start_latitude) * sin(angular_distance) * cos(phi))

    end_longitude = start_longitude + atan2(sin(phi) * sin(angular_distance) * cos(start_latitude),
                                          cos(angular_distance) - sin(start_latitude) * sin(end_latitude))

    return Wgs84Point(degrees(end_latitude), degrees(end_longitude))