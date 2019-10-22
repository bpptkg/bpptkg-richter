import os
import unittest
from richter.link import ArcLinkClient, stream_manager
from richter.utils import find_executable


class ArcLinkTest(unittest.TestCase):

    def test__build_request_file(self):
        client = ArcLinkClient()
        client.request(starttime='2019-01-01 00:00:00',
                       endtime='2019-01-01 01:00:00',
                       network='VG',
                       station='MEPAS',
                       channel='HHZ')
        client.request_file = '/tmp/req.txt'
        client._build_request_file()
        stream_list = '2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n'
        with open('/tmp/req.txt', 'r') as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)

    def test__build_cli(self):
        client = ArcLinkClient()
        cli = ['/usr/bin/python', find_executable('arclink_fetch')]
        self.assertListEqual(client._build_cli(), cli)

    def test__build_cli_arguments(self):
        client = ArcLinkClient()
        client.request_file = '/tmp/req.txt'
        client.output_file = '/tmp/output.mseed'
        options = [
            '--retries=5',
            '--output-file=/tmp/output.mseed',
            '--data-format=mseed',
            '--request-format=native',
            '--timeout=300',
            '/tmp/req.txt',
        ]
        self.assertSetEqual(set(client._build_cli_arguments()), set(options))

    def test_request(self):
        client = ArcLinkClient()
        client.request(starttime='2019-01-01 00:00:00',
                       endtime='2019-01-01 01:00:00',
                       network='VG',
                       station='MEPAS',
                       channel='HHZ')
        stream_list = {
            'starttime': '2019-01-01 00:00:00',
            'endtime': '2019-01-01 01:00:00',
            'network': 'VG',
            'station': 'MEPAS',
            'channel': 'HHZ',
        }
        self.assertDictEqual(client.request_data[0], stream_list)

    def test_request_many(self):
        client = ArcLinkClient()
        client.request_many([
            {'starttime': '2019-01-01 00:00:00',
             'endtime': '2019-01-01 01:00:00',
             'network': 'VG', 'station': 'MEPAS', 'channel': ['HHZ', 'EHZ']},
            {'starttime': '2019-01-01 00:00:00',
             'endtime': '2019-01-01 01:00:00',
             'network': 'VG', 'station': 'MELAB', 'channel': 'HHZ'},
            {'starttime': '2019-01-01 00:00:00',
             'endtime': '2019-01-01 01:00:00',
             'network': 'VG', 'station': 'MEGRA', 'channel': 'HHZ'}
        ])
        client.request_file = '/tmp/req.txt'
        client._build_request_file()
        stream_list = (
            '2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n'
            '2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS EHZ 00\n'
            '2019,01,01,00,00,00 2019,01,01,01,00,00 VG MELAB HHZ 00\n'
            '2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEGRA HHZ 00\n'
        )
        with open('/tmp/req.txt', 'r') as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)


if __name__ == '__main__':
    unittest.main()
