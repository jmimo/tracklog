from collections import namedtuple
from datetime import datetime
from geo import distance, Wgs84Point
import json

BRecord = namedtuple('BRecord', ['datetime', 'point', 'validity', 'baro_altitude', 'gps_altitude'])


def parse(file):
    b_records = list()
    pilot = 'NKN'
    glider = 'NKN'
    instrument = 'NKN'
    with open(file, 'r') as igc:
        for line in igc:
            if line.startswith('HFDTE'):
                date = line[5:11]
            elif line.startswith('HFPLTPILOT') or line.startswith('HPPLTPILOT'):
                pilot = line[11:-1]
            elif line.startswith('HFGTYGLIDERTYPE') or line.startswith('HPGTYGLIDERTYPE'):
                glider = line[16:-1]
            elif line.startswith('HFFTYFRTYPE'):
                instrument = line[12:-1]
            elif line.startswith('AXCT XCTrack'):
                instrument = 'XCTrack'
            elif line.startswith('B'):
                b_records.append(__b_record(date, line))
    return Igc(b_records[0].datetime, pilot, glider, instrument, b_records)


def analyze(igc):
    igc.min_gps_altitude = 5000
    igc.max_gps_altitude = 0
    igc.min_baro_altitude = 5000
    igc.max_baro_altitude = 0
    previous_record = igc.b_records[0]
    for record in igc.b_records:
        if previous_record and previous_record.validity == 'A' and record.validity == 'A':
            igc.tracklog_length += distance(previous_record.point, record.point)
        if igc.min_gps_altitude > record.gps_altitude:
            igc.min_gps_altitude = record.gps_altitude
        if igc.max_gps_altitude < record.gps_altitude:
            igc.max_gps_altitude = record.gps_altitude
        if igc.min_baro_altitude > record.baro_altitude:
            igc.min_baro_altitude = record.baro_altitude
        if igc.max_baro_altitude < record.baro_altitude:
            igc.max_baro_altitude = record.baro_altitude
        previous_record = record

    igc.flight_duration = igc.b_records[-1].datetime - igc.b_records[0].datetime


def __b_record(date, data):
    return BRecord(
        datetime.strptime('{}{}'.format(date, data[1:7]), '%d%m%y%H%M%S'),
        Wgs84Point(
            __latitude_deg(data[7:14], data[14:15]),
            __longitude_deg(data[15:23], data[23:24])
        ),
        data[24:25],
        int(data[25:30]),
        int(data[30:35])
    )


def __latitude_deg(value, cardinal):
    degrees = float(value[0:2])
    minutes = value[2:4]
    fraction = value[4:]

    degrees += (float('{}.{}'.format(minutes, fraction)) / 60)

    return (degrees * -1, degrees)[cardinal == 'N']


def __longitude_deg(value, cardinal):
    degrees = float(value[0:3])
    minutes = value[3:5]
    fraction = value[5:]

    degrees += (float('{}.{}'.format(minutes, fraction)) / 60)

    return (degrees * -1, degrees)[cardinal == 'E']


class Igc:

    def __init__(self, date, pilot, glider, instrument, b_records):
        self.date = date
        self.pilot = pilot
        self.glider = glider
        self.instrument = instrument
        self.b_records = b_records
        self.min_gps_altitude = 0
        self.max_gps_altitude = 0
        self.min_baro_altitude = 0
        self.max_baro_altitude = 0
        self.flight_duration = 0
        self.tracklog_length = 0

    def coordinates_as_json(self):
        coordinates = list()
        for record in self.b_records:
            latitude = float('{:.6f}'.format(record.point.latitude))
            longitude = float('{:.6f}'.format(record.point.longitude))
            coordinates.append({'lat': latitude, 'lng': longitude})
        return json.dumps(coordinates)

    def altitude_as_json(self):
        altitude = list()
        for record in self.b_records:
            altitude.append([record.datetime.strftime('%H:%M:%S'), record.gps_altitude])
        return json.dumps(altitude)
