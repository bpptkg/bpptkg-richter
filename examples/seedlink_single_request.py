
from richter import SeedLinkClient

client = SeedLinkClient(
    address='192.168.0.25:18000',
    data_format='mseed'
)

client.request(
    starttime='2019-01-01 00:00:00',
    endtime='2019-01-01 01:00:00',
    network='VG',
    station='MEPAS',
    channel='HHZ'
)

# See all request data
print(client.request_data)

# Start request to SeedLink server
client.execute()

# See saved data
print(client.output_file)
