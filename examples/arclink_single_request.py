from richter import ArcLinkClient

client = ArcLinkClient(
    address='192.168.0.25:18001',
    user='indrarudianto.official@gmail.com',
    data_format='mseed'
)

client.request(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MEPAS',
    channel='HHZ'
)

# See all request data
print(client.request_data)

# Start request to ArcLink server
client.execute()

# See saved data
print(client.output_file)
