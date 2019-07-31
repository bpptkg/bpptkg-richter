# bpptkg-richter

Python library for computing Richter local magnitude scales on BPPTKG seismic network

## Requirements

* Python 3.5+
* numpy

## Installation

Download the latest version from GitLab repository and unpack the archive:

    tar -xvf bpptkg-richter-v0.1.0.tar.gz

Make Python virtual environment and activate the virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Install dependency packages:

    cd /path/to/bpptkg-richter/
    pip install -r requirements.txt

Install the package:

    python setup.py install

## ArcLink and SeedLink Client

This package provides a wrapper of ArcLink client (via `arclink_fetch`)
and SeedLink client (via `slinktool`) with minimal functional capabilities. Prior
to using the clients, you have to install [SeisComP3](https://www.seiscomp3.org/download.html)
package and add SeisComP3 binaries and Python libaries to `PATH` and `PYTHONPATH`.

1. Edit your `~/.bashrc` and add the following:

        export PATH=$PATH:/path/to/seiscomp3/bin:/path/to/seiscomp3/sbin
        export PYTHONPATH=$PYTHONPATH:/path/to/seiscomp3/lib/python

2. Update user system environment variables:

        source ~/.bashrc

### ArcLink Client

The following provides example of using the client to request data over
ArcLink protocol:

```python
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
```

Required request arguments is `starttime`, `endtime`, `network`, `station`,
and `channel`. You can also add `location` argument (default: 00). It is
optional. Note that all request time is in UTC time zone.

Station channel can be a list of multiple values, for example:

```python
client.request(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MEPAS',
    channel=['HHZ', 'EHZ', 'NHZ']
)
```

After you call `request` method, you have to call `execute` method in order
to make an actual request to the ArcLink server. `execute` method return
Python [CompletedProcess](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess)
and always have return code 0 if request succeed.

Sometime after you call `request` method, you want to edit the request data.
You can call the `request` method again and provide new argument you want
to edit:

```python
client.request(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MEPAS',
    channel=['HHZ', 'EHZ', 'NHZ']
)
print(client.request_data)

# Update station from MEPAS to MELAB
client.request(station='MELAB')
print(client.request_data)
```

If you want to make a bulk request (useful to fetch multi-station data),
you can use `request_many` method and provide a list of dictionary of
request data:

```python
from richter import ArcLinkClient

client = ArcLinkClient(
    address='192.168.0.25:18001',
    user='indrarudianto.official@gmail.com',
    data_format='mseed'
)

client.request_many([
    {
        'starttime': '2019-07-25 00:00:00',
        'endtime': '2019-07-25 01:00:00',
        'network': 'VG',
        'station': 'MEPAS',
        'channel': 'HHZ',
    },
    {
        'starttime': '2019-07-25 00:00:00',
        'endtime': '2019-07-25 01:00:00',
        'network': 'VG',
        'station': 'MELAB',
        'channel': 'HHZ',
    },
    {
        'starttime': '2019-07-25 00:00:00',
        'endtime': '2019-07-25 01:00:00',
        'network': 'VG',
        'station': 'MEGRA',
        'channel': 'HHZ',
    }
])

# See all request data
print(client.request_data)

# Start request to ArcLink server
client.execute()

# See saved data
print(client.output_file)
```

Another way to make bulk request is:

```python

client.request_many(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MEPAS',
    channel='HHZ'
)
client.request_many(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MELAB',
    channel='HHZ'
)
client.request_many(
    starttime='2019-07-25 00:00:00',
    endtime='2019-07-25 01:00:00',
    network='VG',
    station='MEGRA',
    channel='HHZ'
)

client.execute()
```

If you want to edit the request data, you can access `request_data` property
and edit the data you want:

```python
# Update station channel to EHZ of the third request data
client.request_data[2].update(channel='EHZ')
```

### SeedLink Client

Request using SeedLink client is similar with ArcLink client, but SeedLink
client use different data structure. Request using SeedLink client is based-on
single time window for single station or multiple stations request. It differs
from ArcLinkClient that can have different time window for multiple stations
request.

The following provides example of using the client to request data over
SeedLink protocol:

```python
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
```

Required request arguments is `starttime`, `endtime`, `network`, `station`.
You can also add `channel` argument. It is optional. It is also support one
value or a list of multiple values. Note that all request time is in
UTC time zone.

If you want to edit request data, you can all the `request` method again
and provide new keyword argument. It is similar with using ArcLink client:

```python
client.request(
    starttime='2019-07-22 00:00:00',
    endtime='2019-07-22 01:00:00',
    network='VG',
    station='MEPAS',
    channel=['HHZ', 'EHZ', 'NHZ']
)
print(client.request_data)

# Update station from MEPAS to MELAB
client.request(station='MELAB')
print(client.request_data)
```

For bulk request, you can use `request_many` method, but `starttime`, and
`endtime` argument is provided once, and it's used through all request
streams list:

```python
from richter import SeedLinkClient

client = SeedLinkClient(
    address='192.168.0.25:18000',
    data_format='mseed'
)

client.request_many([
    {
        'network': 'VG',
        'station': 'MEPAS',
    },
    {
        'network': 'VG',
        'station': 'MELAB',
        'channel': 'HHZ',
    },
    {
        'network': 'VG',
        'station': 'MEGRA',
        'channel': 'HHZ',
    }
],
    starttime='2019-07-22 00:00:00',
    endtime='2019-07-22 01:00:00'
)

# See all request data
print(client.request_data)

# Start request to SeedLink server
client.execute()

# See saved data
print(client.output_file)
```

Another way to make bulk request is:

```python
# Set request time window
client.request_many(starttime='2019-07-22 00:00:00',
                    endtime='2019-07-22 01:00:00')

# Set streams list
client.request_many(
    network='VG',
    station='MEPAS',
)
client.request_many(
    network='VG',
    station='MELAB',
    channel='HHZ'
)
client.request_many(
    network='VG',
    station='MEGRA',
    channel='HHZ'
)

client.execute()
```

If you want to edit the request data, you can access `request_data` property
and edit the data you want:

```python
# Update station channel to EHZ of the third request data
client.request_data['streams'][2].update(channel='EHZ')
```


## Richter Magnitude Scales

This package also provides a method for computing Richter local
magnitude scales on BPPTKG seismic network (`VG`). Currently supported stations
are `MEDEL`, `MELAB`, `MEPAS`, `MEPUS` and only support `Z` component.

You may want to install [ObsPy](https://www.obspy.org/) package, because
this package only work on ObsPy stream type. Default network is `VG` and
default component is `Z`:

```python
from obspy import read
import richter

stream = read('/path/to/stream.mseed')

# Compute Richter local magnitude for station MEPAS
ml = richter.compute_ml(stream, 'MEPAS', network='VG', component='Z')

# Compute Wood-Anderson zero-to-peak amplitude in meter for station MEPAS
wa_ampl = richter.compute_wa(stream, 'MEPAS', network='VG', component='Z')

# Compute count amplitude peak-to-peak for station MEPAS
app = richter.compute_app(stream, 'MEPAS', network='VG', component='Z')
```

or for short version:

```python
from obspy import read
import richter

stream = read('/path/to/stream.mseed')

ml = richter.compute_ml(stream, 'MEPAS')
wa_ampl = richter.compute_wa(stream, 'MEPAS')
app = richter.compute_app(stream, 'MEPAS')
```

For current version, on computing local magnitude (`compute_ml`) and
Wood-Anderson amplitude(`compute_wa`), supported component is only `Z`
component.

Method `compute_app` support other components, for example:

```python
app = richter.compute_app(stream, 'MELAB', component='E') 
```

## Support

This project is maintained by Indra Rudianto. If you have any question about
this project, you can contact him at <indrarudianto.official@gmail.com>.


## License

Copyright (c) 2019 Balai Penyelidikan dan Pengembangan Teknologi Kebencanaan Geologi (BPPTKG)
