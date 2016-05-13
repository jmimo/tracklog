import unittest
from igc import Wgs84Point
from geo import distance, bearing


class Geo(unittest.TestCase):

    def test_distance(self):
        result = distance(Wgs84Point(46.30440, 8.04091), Wgs84Point(46.56138, 8.33753))
        self.assertAlmostEqual(36513.0, result, delta=0.9)

    def test_bearing(self):
        result = bearing(Wgs84Point(46.30440, 8.04091), Wgs84Point(46.56138, 8.33753))
        self.assertAlmostEqual(0.6701, result, places=4)

        result = bearing(Wgs84Point(46.928876, 8.339587), Wgs84Point(46.945041, 8.427873))
        self.assertAlmostEqual(1.30824, result, places=4)

if __name__ == '__main__':
    unittest.main();
