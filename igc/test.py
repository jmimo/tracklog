import unittest
from igc import parse


class Parser(unittest.TestCase):

    def test_parse(self):
        igc = parse('../test/2015-07-09-Wispile.igc')
        self.assertEqual('Michael Mimo Moratti', igc.pilot)
        self.assertEqual('GIN Boomerang 9', igc.glider)
        self.assertEqual('Flytec, Connect 1', igc.instrument)

    def test_coordinates_as_list(self):
        igc = parse('../test/2015-07-09-Wispile.igc')
        print(igc.coordinates_as_json())

    def test_xctrack(self):
        igc = parse('../test/2015-08-07-Fiesch.igc')
        self.assertEqual('Michael Mimo Moratti', igc.pilot)
        self.assertEqual('XCTrack', igc.instrument)
        self.assertEqual('OZONE Delta 2', igc.glider)
