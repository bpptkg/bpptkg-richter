import os
import pytz
import datetime
import unittest
import bmaclient
from dateutil import parser
from obspy import read

from richter import ml
from richter.link import ArcLinkClient


class TestML(unittest.TestCase):

    def get_starttime_endtime(self, eventdate, duration):
        date_format = '%Y-%m-%d %H:%M:%S'
        start = parser.parse(eventdate).astimezone(pytz.timezone('UTC'))
        end = start + datetime.timedelta(seconds=float(duration))
        return start.strftime(date_format), end.strftime(date_format)

    def test_ml(self):
        api = bmaclient.MonitoringAPI()
        catalog = api.fetch_bulletin(eventdate__gte='2019-07-31',
                                     eventdate__lt='2019-08-01',
                                     eventtype='AWANPANAS')
        client = ArcLinkClient(address='192.168.0.25:18001',
                               user='indrarudianto.official@gmail.com',
                               data_format='mseed')

        for event in catalog:
            start, end = self.get_starttime_endtime(
                event['eventdate'], event['duration'])
            client.request(starttime=start,
                           endtime=end,
                           network='VG',
                           station='MEPAS',
                           channel='HHZ')
            client.output_file = '/tmp/req.mseed'
            client.request_file = '/tmp/req.txt'

            status = client.execute()
            if status.returncode != 0:
                client.clear_request()
                continue
            stream = read(client.output_file)
            self.assertEqual(ml.compute_app(
                stream, 'MEPAS'), event['count_pasarbubar'])
            self.assertAlmostEqual(ml.compute_ml(
                stream, 'MEPAS'), event['ml_pasarbubar'], delta=0.01)
            os.unlink(client.output_file)
            os.unlink(client.request_file)

            client.clear_request()


if __name__ == '__main__':
    unittest.main()
