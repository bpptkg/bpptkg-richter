import os
import unittest
import datetime
from richter.link import ArcLinkClient, stream_manager


class ArcLinkTest(unittest.TestCase):
    def test__build_request_file(self):
        client = ArcLinkClient()
        client.request(
            starttime="2019-01-01 00:00:00",
            endtime="2019-01-01 01:00:00",
            network="VG",
            station="MEPAS",
            channel="HHZ",
        )
        client.request_file = "/tmp/req.txt"
        client._build_request_file()
        stream_list = "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n"
        with open("/tmp/req.txt", "r") as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)

    def test__build_cli_arguments(self):
        client = ArcLinkClient()
        client.request_file = "/tmp/req.txt"
        client.output_file = "/tmp/output.mseed"
        options = [
            "--retries=5",
            "--output-file=/tmp/output.mseed",
            "--data-format=mseed",
            "--request-format=native",
            "--timeout=300",
            "/tmp/req.txt",
        ]
        self.assertSetEqual(set(client._build_cli_arguments()), set(options))

    def test_request(self):
        client = ArcLinkClient()
        client.request(
            starttime="2019-01-01 00:00:00",
            endtime="2019-01-01 01:00:00",
            network="VG",
            station="MEPAS",
            channel="HHZ",
        )
        stream_list = {
            "starttime": "2019-01-01 00:00:00",
            "endtime": "2019-01-01 01:00:00",
            "network": "VG",
            "station": "MEPAS",
            "channel": "HHZ",
        }
        self.assertDictEqual(client.request_data[0], stream_list)

    def test_request_many(self):
        client = ArcLinkClient()
        client.request_many(
            [
                {
                    "starttime": "2019-01-01 00:00:00",
                    "endtime": "2019-01-01 01:00:00",
                    "network": "VG",
                    "station": "MEPAS",
                    "channel": ["HHZ", "EHZ"],
                },
                {
                    "starttime": "2019-01-01 00:00:00",
                    "endtime": "2019-01-01 01:00:00",
                    "network": "VG",
                    "station": "MELAB",
                    "channel": "HHZ",
                },
                {
                    "starttime": "2019-01-01 00:00:00",
                    "endtime": "2019-01-01 01:00:00",
                    "network": "VG",
                    "station": "MEGRA",
                    "channel": "HHZ",
                },
            ]
        )
        client.request_file = "/tmp/req.txt"
        client._build_request_file()
        stream_list = (
            "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n"
            "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS EHZ 00\n"
            "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MELAB HHZ 00\n"
            "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEGRA HHZ 00\n"
        )
        with open("/tmp/req.txt", "r") as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)

    def test_instantiate_class(self):
        client = ArcLinkClient(
            address="192.168.0.25:18001", user="user", data_format="mseed"
        )
        self.assertEqual(client.address, "192.168.0.25:18001")
        self.assertEqual(client.user, "user")
        self.assertEqual(client.data_format, "mseed")

    def test_date_format(self):
        client = ArcLinkClient(
            address="192.168.0.25:18000", user="user", data_format="mseed"
        )

        client.request(
            starttime="2019-01-01 00:00:00",
            endtime="2019-01-01 01:00:00",
            network="VG",
            station="MEPAS",
            channel="HHZ",
        )
        client.request_file = "/tmp/req.txt"
        client._build_request_file()
        stream_list = "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n"
        with open("/tmp/req.txt", "r") as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)

        client.clear_request()
        client.request(
            starttime=datetime.datetime(2019, 1, 1, 0, 0, 0),
            endtime=datetime.datetime(2019, 1, 1, 1, 0, 0),
            network="VG",
            station="MEPAS",
            channel="HHZ",
        )
        client.request_file = "/tmp/req.txt"
        client._build_request_file()
        stream_list = "2019,01,01,00,00,00 2019,01,01,01,00,00 VG MEPAS HHZ 00\n"
        with open("/tmp/req.txt", "r") as buf:
            content = buf.read()
        self.assertEqual(content, stream_list)

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime="", endtime="", network="VG", station="MEPAS", channel="HHZ"
            )
            client.request_file = "/tmp/req.txt"
            client._build_request_file()

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime="2019-10-01 25:12:13",
                endtime="2019-10-01 11:13:13",
                network="VG",
                station="MEPAS",
                channel="HHZ",
            )
            client.request_file = "/tmp/req.txt"
            client._build_request_file()

        with self.assertRaises(ValueError):
            client.clear_request()
            client.request(
                starttime="2019-10-01 11:12:13",
                endtime="2019-10-01 25:13:13",
                network="VG",
                station="MEPAS",
                channel="HHZ",
            )
            client.request_file = "/tmp/req.txt"
            client._build_request_file()


if __name__ == "__main__":
    unittest.main()
