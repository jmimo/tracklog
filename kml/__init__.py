from collections import namedtuple
from math import pi
from geo import point as geo_point, bearing as geo_bearing
from itertools import chain

Polygon = namedtuple('Polygon', ['name', 'points'])
Circle = namedtuple('Circle', ['name', 'description', 'center', 'radius'])
Line = namedtuple('Line', ['name', 'points'])
GoalLine = namedtuple('GoalLine', ['name', 'points'])
GoalHalfCircle = namedtuple('GoalHalfCircle', ['name', 'points'])
Point = namedtuple('Point', ['name', 'point'])


def create_kml(route):
    kml = Kml('{} :: {}'.format(route.competition_name, route.name), 3590)
    line = list()
    for index, turnpoint in enumerate(route.turnpoints):
        kml.add_geo_point('Points', index, turnpoint.circle_point)
        line.append(turnpoint.circle_point)
    kml.add_line('Track', 'optimized', line)
    kml.build('{}-{}.kml'.format(route.competition_name, route.name))


class Kml:

    def __init__(self, name, altitude):
        self.name_ = name
        self.folders_ = dict()
        self.absolute_altitude = altitude

    def add_polygon(self, folder, name, points):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(Polygon(name, points))

    def add_circle(self, folder, name, description, point, radius):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(Circle(name, description, point, radius))

    def add_line(self, folder, name, points):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(Line(name, points))

    def add_goal_line(self, folder, name, points):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(GoalLine(name, points))

    def add_goal_half_circle(self, folder, name, points):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(GoalHalfCircle(name, points))

    def add_point(self, folder, name, point):
        if folder not in self.folders_:
            self.folders_[folder] = list()
        self.folders_[folder].append(point(name, point))

    def build(self, file_name):
        kml = self.__header()
        for name, folder in self.folders_.items():
            kml = chain(kml, self.__folder(name, folder))
        kml = chain(kml, self.__footer())
        file = open(file_name, 'w')
        for line in kml:
            file.write(line + '\n')
        file.close()

    def __folder(self, name, folder):
        yield '<Folder>'
        yield '<name>{}</name>'.format(name)
        for item in folder:
            if isinstance(item, Polygon):
                yield from self.__polygon(item)
            if isinstance(item, Circle):
                yield from self.__circle(item)
            if isinstance(item, Line):
                yield from self.__line(item)
            if isinstance(item, Point):
                yield from self.__point(item)
            if isinstance(item, GoalLine):
                yield from self.__goal_line(item)
            if isinstance(item, GoalHalfCircle):
                yield from self.__goal_half_circle(item)
        yield '</Folder>'

    def __circle(self, circle):
        yield '<Placemark>'
        yield '<name>{}</name>'.format(circle.name)
        yield '<description>{}</description>'.format(circle.description)
        yield '<styleUrl>#default</styleUrl>'
        yield '<Polygon>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<outerBoundaryIs>'
        yield '<LinearRing>'
        yield '<coordinates>'

        steps = 80
        phi_step = (2 * pi) / steps
        phi = phi_step
        for n in range(steps + 1):
            point = geo_point(circle.center, circle.radius, phi)
            phi += phi_step
            yield '{},{},{}'.format(point.longitude, point.latitude, self.absolute_altitude)

        yield '</coordinates>'
        yield '</LinearRing>'
        yield '</outerBoundaryIs>'
        yield '</Polygon>'
        yield '</Placemark>'

    def __goal_line(self, goalline):
        turnpoint = goalline.points[0]
        goal = goalline.points[1]
        bearing = geo_bearing(turnpoint.point, goal.point)
        line_start = geo_point(goal.point, goal.radius, bearing + (pi / 2))
        line_end = geo_point(goal.point, goal.radius, bearing - (pi / 2))
        yield '<Placemark>'
        yield '<name>{}</name>'.format(goalline.name)
        yield '<styleUrl>#default</styleUrl>'
        yield '<LineString>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<coordinates>'
        yield '{},{},{}'.format(line_start.longitude, line_start.latitude, self.absolute_altitude)
        yield '{},{},{}'.format(line_end.longitude, line_end.latitude, self.absolute_altitude)
        yield '</coordinates>'
        yield '</LineString>'
        yield '</Placemark>'

    def __goal_half_circle(self, goalhalfcircle):
        turnpoint = goalhalfcircle.points[0]
        goal = goalhalfcircle.points[1]
        bearing = geo_bearing(turnpoint.point, goal.point)
        circle_start = geo_point(goal.point, goal.radius, bearing + (pi / 2))
        start_bearing = bearing(goal.point, circle_start)
        yield '<Placemark>'
        yield '<name>{}</name>'.format(goalhalfcircle.name)
        yield '<styleUrl>#default</styleUrl>'
        yield '<Polygon>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<outerBoundaryIs>'
        yield '<LinearRing>'
        yield '<coordinates>'

        steps = 40
        phi_step = pi / steps
        phi = start_bearing
        for n in range(steps + 1):
            point = geo_point(goal.point, goal.radius, phi)
            phi -= phi_step
            yield '{},{},{}'.format(point.longitude, point.latitude, self.absolute_altitude)
        yield '{},{},{}'.format(circle_start.longitude, circle_start.latitude, self.absolute_altitude)
        yield '</coordinates>'
        yield '</LinearRing>'
        yield '</outerBoundaryIs>'
        yield '</Polygon>'
        yield '</Placemark>'

    def __polygon(self, polygon):
        yield '<Placemark>'
        yield '<name>{}</name>'.format(polygon.name)
        yield '<styleUrl>#default</styleUrl>'
        yield '<Polygon>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<outerBoundaryIs>'
        yield '<LinearRing>'
        yield '<coordinates>'
        for entry in reversed(polygon.points):
            yield '{},{},{}'.format(entry.longitude, entry.latitude, self.absolute_altitude)
        yield '</coordinates>'
        yield '</LinearRing>'
        yield '</outerBoundaryIs>'
        yield '</Polygon>'
        yield '</Placemark>'

    def __line(self, line):
        yield '<Placemark>'
        yield '<name>{}</name>'.format(line.name)
        yield '<styleUrl>#track</styleUrl>'
        yield '<LineString>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<coordinates>'
        for entry in line.points:
            yield '{},{},{}'.format(entry.longitude, entry.latitude, self.absolute_altitude)
        yield '</coordinates>'
        yield '</LineString>'
        yield '</Placemark>'

    def __geo_point(self, point):
        yield '<Placemark>'
        yield '<name>{}</name>'.format(point.name)
        yield '<styleUrl>#s_blue-pushpin</styleUrl>'
        yield '<Point>'
        yield '<extrude>0</extrude>'
        yield '<altitudeMode>absolute</altitudeMode>'
        yield '<coordinates>{},{},{}</coordinates>'.format(point.point.longitude, point.point.latitude, self.absolute_altitude)
        yield '</Point>'
        yield '</Placemark>'

    def __header(self):
        yield '<?xml version="1.0" encoding="UTF-8"?>'
        yield '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" ' \
              'xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">'
        yield '<Document>'
        yield '<name>{}</name>'.format(self.name_)
        yield '<StyleMap id="default">'
        yield '<Pair>'
        yield '<key>normal</key>'
        yield '<styleUrl>#default0</styleUrl>'
        yield '</Pair>'
        yield '<Pair>'
        yield '<key>highlight</key>'
        yield '<styleUrl>#hl</styleUrl>'
        yield '</Pair>'
        yield '</StyleMap>'
        yield '<StyleMap id="track">'
        yield '<Pair>'
        yield '<key>normal</key>'
        yield '<styleUrl>#line</styleUrl>'
        yield '</Pair>'
        yield '<Pair>'
        yield '<key>highlight</key>'
        yield '<styleUrl>#hl</styleUrl>'
        yield '</Pair>'
        yield '</StyleMap>'
        yield '<Style id="default0">'
        yield '<LineStyle>'
        yield '<color>ff2f1eff</color>'
        yield '</LineStyle>'
        yield '<PolyStyle>'
        yield '<color>662b1dff</color>'
        yield '</PolyStyle>'
        yield '</Style>'
        yield '<Style id="hl">'
        yield '<IconStyle>'
        yield '<scale>1.2</scale>'
        yield '</IconStyle>'
        yield '<LineStyle>'
        yield '<color>ff2f1eff</color>'
        yield '</LineStyle>'
        yield '<PolyStyle>'
        yield '<color>662b1dff</color>'
        yield '</PolyStyle>'
        yield '</Style>'
        yield '<Style id="line">'
        yield '<LineStyle>'
        yield '<color>ff00aaff</color>'
        yield '<width>2</width>'
        yield '</LineStyle>'
        yield '<PolyStyle>'
        yield '<color>662b1dff</color>'
        yield '</PolyStyle>'
        yield '</Style>'
        yield '<Style id="s_blue-pushpin">'
        yield '<IconStyle>'
        yield '<Icon>'
        yield '<href>http://maps.google.com/mapfiles/kml/pushpin/blue-pushpin.png</href>'
        yield '</Icon>'
        yield '</IconStyle>'
        yield '</Style>'

    def __footer(self):
        yield '</Document>'
        yield '</kml>'
