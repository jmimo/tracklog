from geo import Wgs84Point
from math import sin, cos, atan2, sqrt, asin, radians, degrees, pi

EARTH_RADIUS_IN_METERS = 6371000


def distance(start, end):
    """
    https://en.wikipedia.org/wiki/Haversine_formula
    """
    start_latitude = radians(start.latitude)
    start_longitude = radians(start.longitude)
    end_latitude = radians(end.latitude)
    end_longitude = radians(end.longitude)
    distance_latitude = end_latitude - start_latitude
    distance_longitude = end_longitude - start_longitude

    angle = sin(distance_latitude / 2) * sin(distance_latitude / 2) + \
            cos(start_latitude) * cos(end_latitude) * \
            sin(distance_longitude / 2) * sin(distance_longitude / 2)

    radDistance = 2 * atan2(sqrt(angle), sqrt(1 - angle))

    return EARTH_RADIUS_IN_METERS * radDistance


def bearing_between_two_points(start, end):
    """
    calculates a bearing in radians corrected for +/- pi orientation to always be positive.
    """
    start_latitude = radians(start.latitude)
    start_longitude = radians(start.longitude)
    end_latitude = radians(end.latitude)
    end_longitude = radians(end.longitude)

    y = sin(end_longitude - start_longitude) * cos(end_latitude)
    x = cos(start_latitude) * sin(end_latitude) - \
        sin(start_latitude) * cos(end_latitude) * \
        cos(end_longitude - start_longitude)
    bearing = atan2(y, x)
    return bearing if bearing >= 0 else (2 * pi) + bearing


def point_from_distance_and_bearing(start, distance, phi):
    """
    calculates a point in lat/lon from a start point distance and bearing in radians
    """
    start_latitude = radians(start.latitude)
    start_longitude = radians(start.longitude)
    angular_distance = distance / EARTH_RADIUS_IN_METERS

    end_latitude = asin(sin(start_latitude) * cos(angular_distance) +
                       cos(start_latitude) * sin(angular_distance) * cos(phi))

    end_longitude = start_longitude + atan2(sin(phi) * sin(angular_distance) * cos(start_latitude),
                                          cos(angular_distance) - sin(start_latitude) * sin(end_latitude))

    return Wgs84Point(degrees(end_latitude), degrees(end_longitude))


def find_tangential_point(start, intermediate, end, radius):
    """
    calculates the node radius tangential point from the bisecting angle a -> b <- c
    """
    start_bearing = bearing_between_two_points(intermediate, start)
    end_bearing = bearing_between_two_points(intermediate, end)

    phi = bisect(start_bearing, end_bearing)
    return point_from_distance_and_bearing(intermediate, radius, phi)


def distance_from_point_to_line(point, line_start, line_end):
    """
    calculates the distance form a point to a line and delivers a point on that line from the distance.
    """
    distance_start_to_point = distance(line_start, point)
    start_end_angle = bearing_between_two_points(line_start, line_end)
    start_point_angle = bearing_between_two_points(line_start, point)
    phi = angle_delta(start_point_angle, start_end_angle)

    adjacent = abs(distance_start_to_point * cos(phi))
    interpolation_point = point_from_distance_and_bearing(line_start, adjacent, start_end_angle)
    dist = distance(point, interpolation_point)

    return interpolation_point, dist


def point_on_circle_from_intersection(line_start, line_end, interpolation_point, distance, radius):
    """
    finds the point where the line from the start point intersects the node b cylinder.
    this will only work if the distance is shorter than the radius!
    """
    if distance >= radius:
        raise Exception('Unable to determine intersection point when the distance is >= radius!')
    return point_from_distance_and_bearing(interpolation_point, sqrt(radius ** 2 - distance ** 2),
                                           bearing_between_two_points(line_end, line_start))


def angle_delta(start, end):
    """
    calculates the delta radians between two radian values.
    i.e.: a = 0.4 b = 2.4 a to be == 2 radians.
    this method compensates the 2pi (zero) point.
    """
    return min((2 * pi) - abs(start - end), abs(start - end))


def bisect(start, end):
    """
    bisection of two radian angles.
    """
    delta = angle_delta(start, end)
    phi = delta / 2

    min_angle = min(start, end)
    max_angle = max(start, end)

    if max_angle > (3 * pi) / 2 and min_angle < (pi / 2):
        if max_angle + phi < (2 * pi):
            return max_angle + phi
        else:
            return min_angle - phi
    else:
        return max_angle - phi
