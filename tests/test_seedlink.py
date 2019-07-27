import unittest
from richter.link import SeedLinkClient
from richter.utils import find_executable


class SeedLinkClientTest(unittest.TestCase):

    def test__build_stream_list(self):
        client = SeedLinkClient()
        client.request(network='VG', station='MEPAS', channel=['HHZ', 'EHZ'])
        stream_list = 'VG_MEPAS:HHZ EHZ'
        self.assertEqual(client._build_stream_list(), stream_list)

        client.clear_request()
        client.request_many(streams=[
            {'network': 'VG', 'station': 'MEPAS', 'channel': ['HHZ', 'EHZ']},
            {'network': 'VG', 'station': 'MELAB', 'channel': 'HHZ'},
            {'network': 'VG', 'station': 'MEGRA'}
        ])
        stream_list = 'VG_MEPAS:HHZ EHZ,VG_MELAB:HHZ,VG_MEGRA'
        self.assertEqual(client._build_stream_list(), stream_list)

    def test__build_time_window(self):
        client = SeedLinkClient()
        client.request(starttime='2019-01-01 00:00:00')
        time_window = '2019,01,01,00,00,00:'
        self.assertEqual(client._build_time_window(), time_window)

        client.clear_request()
        client.request(starttime='2019-01-01 00:00:00',
                       endtime='2019-01-01 01:00:00')
        time_window = '2019,01,01,00,00,00:2019,01,01,01,00,00'
        self.assertEqual(client._build_time_window(), time_window)

        client.clear_request()
        client.request_many(starttime='2019-01-01 00:00:00',
                            endtime='2019-01-01 01:00:00')
        time_window = '2019,01,01,00,00,00:2019,01,01,01,00,00'
        self.assertEqual(client._build_time_window(), time_window)

    def test__build_cli(self):
        client = SeedLinkClient()
        self.assertListEqual(client._build_cli(),
                         [find_executable(client.seedlink_cli)])

    def test__build_cli_arguments(self):
        client = SeedLinkClient()
        client.request(starttime='2019-01-01 00:00:00',
                       endtime='2019-01-01 01:00:00')
        client.request(network='VG', station='MEPAS', channel=['HHZ', 'EHZ'])
        client.output_file = '/tmp/data.mseed'
        cli_arguments = [
            '-nd', 30,
            '-nt', 60,
            '-tw', '2019,01,01,00,00,00:2019,01,01,01,00,00',
            '-S', 'VG_MEPAS:HHZ EHZ',
            '-o', '/tmp/data.mseed',
        ]
        self.assertListEqual(client._build_cli_arguments(), cli_arguments)


if __name__ == '__main__':
    unittest.main()
