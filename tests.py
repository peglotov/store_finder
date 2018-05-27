import unittest
import subprocess
import tempfile
import mock
from subprocess import CalledProcessError
from find_store import find_closest_store
from find_store import get_args_dict


def mocked_requests_get(*args, **kwargs):

    class MockResponse:

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0].startswith('https://locationiq.org/v1/search.php?'):
        return MockResponse([{u'display_name': u'Market Street, Hayes Valley, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'179731199', u'lon': u'-122.4247604', u'lat': u'37.7707177', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'512874166', u'boundingbox': [u'37.7706943', u'37.7707177', u'-122.4247874', u'-122.4247604'], u'type': u'primary', u'class': u'highway'}, {u'display_name': u'Market Street, Duboce Triangle, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'179920045', u'lon': u'-122.4327512', u'lat': u'37.7644146', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'514598270', u'boundingbox': [u'37.7642405', u'37.7644146', u'-122.4329602', u'-122.4327512'], u'type': u'primary', u'class': u'highway'}, {u'display_name': u'Market Street, Cole Valley, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'179821053', u'lon': u'-122.4449856', u'lat': u'37.759206', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'513698390', u'boundingbox': [u'37.7590809', u'37.7593544', u'-122.4449856', u'-122.4449722'], u'type': u'primary', u'class': u'highway'}, {u'display_name': u'Market Street, Castro District, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'181146457', u'lon': u'-122.4372984', u'lat': u'37.761863', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'525599651', u'boundingbox': [u'37.7616774', u'37.761863', u'-122.4383773', u'-122.4372984'], u'type': u'primary', u'class': u'highway'}, {u'display_name': u'Market Street, Civic Center, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'188071017', u'lon': u'-122.4178444', u'lat': u'37.7763691', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'571967391', u'boundingbox': [u'37.7757055', u'37.7763691', u'-122.418695', u'-122.4178444'], u'type': u'secondary', u'class': u'highway'}, {u'display_name': u'Market Street, Tenderloin, San Francisco, San Francisco City and County, California, 94114, United States of America', u'importance': 0.425, u'place_id': u'179822198', u'lon': u'-122.4124836', u'lat': u'37.7804523', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'513704174', u'boundingbox': [u'37.7804523', u'37.7818126', u'-122.4124836', u'-122.4107575'], u'type': u'secondary', u'class': u'highway'}, {u'display_name': u'Market Street, Financial District, San Francisco, San Francisco City and County, California, 94111, United States of America', u'importance': 0.425, u'place_id': u'181751063', u'lon': u'-122.3964008', u'lat': u'37.7932487', u'osm_type': u'way', u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', u'osm_id': u'530178868', u'boundingbox': [u'37.793125', u'37.7933542', u'-122.3965374', u'-122.3962778'], u'type': u'tertiary', u'class': u'highway'}], 200)

    return MockResponse(None, 404)


class TestFindStore(unittest.TestCase):

    def setUp(self):
        self.stderr = tempfile.TemporaryFile()
        self.command = './find_store.py'
        self.address = '"1200 Market St., San Francisco, CA"'
        self.zip = '"94114"'

    def tearDown(self):
        self.stderr.close()

    def test_args_parser_help(self):
        output = subprocess.check_output([self.command, '-h'])
        self.assertTrue(output.find('Find closest store.') > -1, 'help output error')

    def test_args_parser_address_or_zip_required(self):
        try:
            subprocess.check_output([self.command], stderr=self.stderr)
        except CalledProcessError as e:
            self.assertGreater(e.returncode, 0, 'return code is 0')
            self.stderr.seek(0)
            self.assertTrue(self.stderr.read().find('required') > -1, 'address or zip is required')

    @mock.patch('find_store.requests.get', side_effect=mocked_requests_get)
    def test_process_address(self, mock_get):
        args_dict = get_args_dict(['--address={}'.format(self.address)])
        result = find_closest_store(args_dict)
        self.assertTrue('distance' in result, 'should process address')
        self.assertEqual(len(mock_get.call_args_list), 1)

    @mock.patch('find_store.requests.get', side_effect=mocked_requests_get)
    def test_process_zip(self, mock_get):
        args_dict = get_args_dict(['--zip={}'.format(self.zip)])
        result = find_closest_store(args_dict)
        self.assertTrue('distance' in result, 'should process address')
        self.assertEqual(len(mock_get.call_args_list), 1)

    def test_cant_be_both(self):
        try:
            subprocess.check_output([self.command, '--address={}'.format(self.address), '--zip={}'.format(self.zip)], stderr=self.stderr)
        except CalledProcessError as e:
            self.assertGreater(e.returncode, 0, 'return code is 0')
            self.stderr.seek(0)
            self.assertTrue(self.stderr.read().find('error: argument --zip: not allowed with argument --address') > -1, 'cant be both address and zip')

    @mock.patch('find_store.requests.get', side_effect=mocked_requests_get)
    def test_outputs_closest_in_units(self, mock_get):
        args_dict = get_args_dict(['--address={}'.format(self.address), '--units=km'])
        result = find_closest_store(args_dict)
        self.assertTrue(result['units'] == 'km', "should output distance in km")
        args_dict = get_args_dict(['--address={}'.format(self.address), '--units=mi'])
        result = find_closest_store(args_dict)
        self.assertTrue(result['units'] == 'mi', "should output distance in mi")
        self.assertEqual(len(mock_get.call_args_list), 2)


if __name__ == '__main__':
    unittest.main()
