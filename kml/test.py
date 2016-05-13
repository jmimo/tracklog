import unittest
from kml import Kml
from igc import Wgs84Point


class KmlTest(unittest.TestCase):

    def test_circle(self):
        kml = Kml('CircleTest', 2000)
        kml.add_circle('Test', 'Pilatus', 'some description', Wgs84Point(46.978308, 8.254787), 1000)
        kml.build('circle-test.kml')

    def test_line(self):
        kml = Kml('LineTest', 2000)

        points = [
            Wgs84Point(46.941800, 8.116400),
            Wgs84Point(46.978308, 8.254787),
            Wgs84Point(46.928876, 8.339587),
        ]

        kml.add_line('Test', 'Track', points)
        kml.build('line-test.kml')
