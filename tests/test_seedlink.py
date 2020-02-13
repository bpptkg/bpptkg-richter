import unittest
import datetime
from richter.link import SeedLinkClient, LinkError


class SeedLinkClientTest(unittest.TestCase):

    def test__build_stream_list(self):
        client = SeedLinkClient()
        client.request(network='VG', station='MEPAS', channel=['HHZ', 'EHZ'])
        stream_list = 'VG_MEPAS:HHZ EHZ'
        self.assertEqual(client._build_stream_list(), stream_list)

        client.clear_request()
        client.request_many([
            {'network': 'VG', 'station': 'MEPAS', 'channel': ['HHZ', 'EHZ']},
            {'network': 'VG', 'station': 'MELAB', 'channel': 'HHZ'},
            {'network': 'VG', 'station': 'MEGRA'}
        ])
        stream_list = 'VG_MEPAS:HHZ EHZ,VG_MELAB:HHZ,VG_MEGRA'
        self.assertEqual(client._build_stream_list(), stream_list)

    def test__build_time_window(self):
        client = SeedLinkClient()
        client.request(starttime='2019-01-01 00:00:00',
                       endtime='2019-01-01 01:00:00')
        time_window = '2019,01,01,00,00,00:2019,01,01,01,00,00'
        self.assertEqual(client._build_time_window(), time_window)

        client.clear_request()
        client.request_many(starttime='2019-01-01 00:00:00',
                            endtime='2019-01-01 01:00:00')
        time_window = '2019,01,01,00,00,00:2019,01,01,01,00,00'
        self.assertEqual(client._build_time_window(), time_window)

    def test__build_cli_arguments(self):
        client = SeedLinkClient(address='192.168.0.25:18000')
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
            '192.168.0.25:18000',
        ]
        self.assertListEqual(client._build_cli_arguments(), cli_arguments)

    def test_instantiate_class(self):
        client = SeedLinkClient(
            address='192.168.0.25:18000',
            data_format='mseed'
        )
        self.assertEqual(client.address, '192.168.0.25:18000')
        self.assertEqual(client.data_format, 'mseed')

    def test__check_required(self):
        client = SeedLinkClient(address='192.168.0.25:18000',
                                data_format='mseed')

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request()
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request(
                starttime='2019-01-01 12:00:00',
                endtime='2019-01-01 12:01:00'
            )
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request(
                starttime='2019-01-01 12:00:00',
                endtime='2019-01-01 12:01:00',
                network='VG',
            )
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

    def test__check_required_request_many(self):
        client = SeedLinkClient(address='192.168.0.25:18000',
                                data_format='mseed')

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request_many()
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request_many(
                starttime='2019-01-01 12:00:00',
                endtime='2019-01-01 12:01:00'
            )
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

        with self.assertRaises(LinkError):
            client.clear_request()
            client.request_many(
                starttime='2019-01-01 12:00:00',
                endtime='2019-01-01 12:01:00',
                network='VG',
            )
            client._check_request_parameters()
            client._build_cli_with_arguments()
            client._check_required()

    def test_date_format(self):
        client = SeedLinkClient(address='192.168.0.25:18000',
                                data_format='mseed')

        client.request(
            starttime='2019-10-01 11:12:13',
            endtime='2019-10-01 11:13:13',
            network='VG',
            station='MEPAS'
        )
        time_window = '2019,10,01,11,12,13:2019,10,01,11,13,13'
        self.assertEqual(client._build_time_window(), time_window)

        client.clear_request()
        client.request(
            starttime=datetime.datetime(2019, 10, 1, 11, 12, 13),
            endtime=datetime.datetime(2019, 10, 1, 11, 13, 13),
            network='VG',
            station='MEPAS'
        )
        time_window = '2019,10,01,11,12,13:2019,10,01,11,13,13'
        self.assertEqual(client._build_time_window(), time_window)

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime='2019-10-01 25:12:13',
                endtime='2019-10-01 11:13:13',
                network='VG',
                station='MEPAS'
            )
            time_window = '2019,10,01,11,12,13:2019,10,01,11,13,13'
            self.assertEqual(client._build_time_window(), time_window)

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime='2019-10-01 11:12:13',
                endtime='2019-10-01 25:13:13',
                network='VG',
                station='MEPAS'
            )
            time_window = '2019,10,01,11,12,13:2019,10,01,11,13,13'
            self.assertEqual(client._build_time_window(), time_window)

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime='',
                endtime='',
                network='VG',
                station='MEPAS'
            )
            time_window = '2019,10,01,11,12,13:2019,10,01,11,13,13'
            self.assertEqual(client._build_time_window(), time_window)


if __name__ == '__main__':
    unittest.main()
