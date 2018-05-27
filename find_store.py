#!/usr/bin/env python

import argparse
import csv
import requests
import geopy.distance
import json


def get_latlon(location):
    response = requests.get('https://locationiq.org/v1/search.php?key=98b7d5eb28a80e&format=json&q=' + location)
    json = response.json()[0]
    return (json['lat'], json['lon'])


def parse_args(args):
    parser = argparse.ArgumentParser(description="Find closest store.")
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument('--address', type=str, help='address')
    location_group.add_argument('--zip', type=str, help='zip code')
    parser.add_argument('--units', type=str, help='distance units', choices=['mi', 'km'], default='mi')
    parser.add_argument('--output', type=str, help='output format', choices=['text', 'json'], default='text')
    return parser.parse_args(args)


class StoreLocations:

    def __init__(self, file_name):
        self.locations = []
        with open(file_name, 'rU') as csv_file:
            store_locations_reader = csv.reader(csv_file)
            store_locations_reader.next()
            for row in store_locations_reader:
                location = {}
                location['row'] = row
                location['latlon'] = (float(row[6]), float(row[7]))
                self.locations.append(location)

    def find_closest(self, latlon):
        min_distance = 1e6
        min_location = None
        for location in self.locations:
            distance = geopy.distance.distance(location['latlon'], latlon)
            if distance < min_distance:
                min_distance = distance
                min_location = location
        return (min_distance, min_location)


def find_closest_store(args_dict):
    store_locations = StoreLocations('./store-locations.csv')
    location = args_dict.get('address') if args_dict.get('address') else args_dict.get('zip')
    latlon = get_latlon(location)
    distance, closest_location = store_locations.find_closest(latlon)
    row = closest_location['row']
    address = row[2] + ', ' + row[3] + ', ' + row[4] + ' ' + row[5]
    return {
        'distance': getattr(distance, args_dict['units']),
        'units': args_dict['units'],
        'address': address
    }


def get_args_dict(args=None):
    return vars(parse_args(args))


if __name__ == '__main__':
    args_dict = get_args_dict()

    result = find_closest_store(args_dict)

    if args_dict['output'] == 'text':
        print 'distance: {}{}, address: {}'.format(result['distance'], result['units'], result['address'])
    else:
        print json.dumps(result)
