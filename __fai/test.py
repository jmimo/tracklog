import unittest
from geo import Wgs84Point
from __fai import distance, bearing_between_two_points, point_from_distance_and_bearing, distance_from_point_to_line, angle_delta, find_tangential_point, bisect
from math import pi
from kml import Kml
from kml import create_kml


class TestFaiDistanceCalculation(unittest.TestCase):

    def test_example(self):
        result = distance(Wgs84Point(46.30440, 8.04091), Wgs84Point(46.56138, 8.33753))
        self.assertAlmostEqual(36513.0, result, delta=0.9)


class Bearing(unittest.TestCase):

    def test_bearing(self):
        kml = Kml('BearingTest', 2500)
        point = Wgs84Point(46.978308, 8.254787)

        step = pi / 12
        bearing = 0

        for n in range(24):
            new_point = point_from_distance_and_bearing(point, 2000, bearing)
            new_bearing = bearing_between_two_points(point, new_point)
            print('step: {}, bearing: {}, calculated bearing: {} to point: {}'.format(n, bearing, new_bearing, new_point))
            self.assertAlmostEqual(bearing, new_bearing, places=4)
            kml.add_point('Bearing', '{}'.format(n), new_point)
            bearing += step
        kml.build('BearingTest.kml')

    def test_example(self):
        result = bearing_between_two_points(Wgs84Point(46.30440, 8.04091), Wgs84Point(46.56138, 8.33753))
        self.assertAlmostEqual(0.6701, result, places=4)

        result = bearing_between_two_points(Wgs84Point(46.928876, 8.339587), Wgs84Point(46.945041, 8.427873))
        self.assertAlmostEqual(1.30824, result, places=4)


class TestPointFromDistanceAndBearing(unittest.TestCase):

    def test_example(self):
        point = point_from_distance_and_bearing(Wgs84Point(46.56138, 8.33753), 23000, 0)
        self.assertAlmostEqual(46.768333, point.latitude, places=3)
        self.assertAlmostEqual(8.3375, point.longitude, places=3)


class TestDistanceFromPointToLine(unittest.TestCase):

    def test_wgs(self):
        point = Wgs84Point(47.056291, 8.485030)  # Rigi Kulm
        start = Wgs84Point(46.979779, 8.254495)  # Pilatus
        end = Wgs84Point(46.929596, 8.339708)  # Stanserhorn

        result = distance_from_point_to_line(point, start, end)
        self.assertAlmostEqual(17865, result[1], places=0)
        self.assertAlmostEqual(46.9347, result[0].latitude, places=3)
        self.assertAlmostEqual(8.3308, result[0].longitude, places=3)


class TestDelta(unittest.TestCase):

    def test_clockwise_increments(self):
        step = pi / 12
        start = (2 * pi) - step
        end = step

        for n in range(23):
            self.assertAlmostEqual(0.5235987755982983, angle_delta(start, end), places=6)
            start += step
            end += step

    def test_counterclockwise_increments(self):
        step = pi / 12
        start = (2 * pi) - step
        end = step

        for n in range(23):
            self.assertAlmostEqual(0.5235987755982983, angle_delta(start, end), places=6)
            start -= step
            end -= step

    def test_opening_angle(self):
        step = pi / 12
        start = (2 * pi) - step
        end = step
        assertion_step = 0.5235987755982983
        assertion = assertion_step
        direction = True

        for n in range(23):
            self.assertAlmostEqual(assertion, angle_delta(start, end), places=6, msg='step: {}'.format(n))
            start -= step
            end += step
            if n != 0 and (n + 1) % 6 == 0:
                direction = (True, False)[direction]

            if direction:
                assertion += assertion_step
            else:
                assertion -= assertion_step


class TestTangentialPoint(unittest.TestCase):

    def test_northern_turnpoint(self):
        start = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        intermediate = Turnpoint(name='Meggen', point=Wgs84Point(47.046134, 8.363826), radius=1000)
        end = Turnpoint(name='Buochserhorn', point=Wgs84Point(46.945041, 8.427873), radius=1000)

        start_bearing = bearing_between_two_points(intermediate.point, start.point)
        end_bearing = bearing_between_two_points(intermediate.point, end.point)

        print('bearing start -> intermediate: {}, intermediate -> end: {}'.format(start_bearing, end_bearing))

        phi = bisect(start_bearing, end_bearing)

        print('phi: {}'.format(phi))

        point = point_from_distance_and_bearing(intermediate.point, intermediate.radius, phi)

        intermediate.circle_point = point

        create_route_kml('northern-turnpoint', [start, intermediate, end])

    def test_southern_turnpoint(self):
        start = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        intermediate = Turnpoint(name='Schluchberg', point=Wgs84Point(46.866398, 8.333957), radius=1000)
        end = Turnpoint(name='Buochserhorn', point=Wgs84Point(46.945041, 8.427873), radius=1000)

        start_bearing = bearing_between_two_points(intermediate.point, start.point)
        end_bearing = bearing_between_two_points(intermediate.point, end.point)

        print('bearing start -> intermediate: {}, intermediate -> end: {}'.format(start_bearing, end_bearing))

        phi = bisect(start_bearing, end_bearing)

        print('phi: {}'.format(phi))

        point = point_from_distance_and_bearing(intermediate.point, intermediate.radius, phi)

        intermediate.circle_point = point

        create_route_kml('southern-turnpoint', [start, intermediate, end])

    def test_tangential_point_north(self):
        start = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        intermediate = Turnpoint(name='Stanserhorn', point=Wgs84Point(46.928876, 8.339587), radius=1000)
        end = Turnpoint(name='Buochserhorn', point=Wgs84Point(46.945041, 8.427873), radius=1000)

        intermediate.circle_point = find_tangential_point(start.point, intermediate.point, end.point,
                                                                      intermediate.radius)
        create_route_kml('north-point', [start, intermediate, end])
        self.assertAlmostEqual(46.9376, intermediate.circle_point.latitude, places=4)
        self.assertAlmostEqual(8.3424, intermediate.circle_point.longitude, places=3)

    def test_tangential_point_north_reversed(self):
        start = Turnpoint(name='Buochserhorn', point=Wgs84Point(46.945041, 8.427873), radius=1000)
        intermediate = Turnpoint(name='Stanserhorn', point=Wgs84Point(46.928876, 8.339587), radius=1000)
        end = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        intermediate.circle_point = find_tangential_point(start.point, intermediate.point, end.point,
                                                                      intermediate.radius)
        create_route_kml('north-point-reversed', [start, intermediate, end])
        self.assertAlmostEqual(46.9376, intermediate.circle_point.latitude, places=4)
        self.assertAlmostEqual(8.3424, intermediate.circle_point.longitude, places=3)

    def test_tangential_point_south(self):
        start = Turnpoint(name='Schimbrig', point=Wgs84Point(46.941800, 8.116400), radius=1000)
        intermediate = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        end = Turnpoint(name='Stanserhorn', point=Wgs84Point(46.928876, 8.339587), radius=1000)
        intermediate.circle_point = find_tangential_point(start.point, intermediate.point, end.point,
                                                                      intermediate.radius)
        create_route_kml('south-point', [start, intermediate, end])
        self.assertAlmostEqual(46.9694, intermediate.circle_point.latitude, places=4)
        self.assertAlmostEqual(8.2525, intermediate.circle_point.longitude, places=3)

    def test_tangential_point_south_reversed(self):
        start = Turnpoint(name='Stanserhorn', point=Wgs84Point(46.928876, 8.339587), radius=1000)
        intermediate = Turnpoint(name='Pilatus', point=Wgs84Point(46.978308, 8.254787), radius=1000)
        end = Turnpoint(name='Schimbrig', point=Wgs84Point(46.941800, 8.116400), radius=1000)
        intermediate.circle_point = find_tangential_point(start.point, intermediate.point, end.point,
                                                                      intermediate.radius)
        create_route_kml('south-point-reversed', [start, intermediate, end])
        self.assertAlmostEqual(46.9694, intermediate.circle_point.latitude, places=4)
        self.assertAlmostEqual(8.2525, intermediate.circle_point.longitude, places=3)


def create_route_kml(name, turnpoints):
    route = Route(turnpoints)
    route.competition_name = 'Basetest'
    route.name = name
    create_kml(route)

if __name__ == '__main__':
    unittest.main();
