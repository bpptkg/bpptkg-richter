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
print(client.requests)

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
print(client.requests)

# Update station from MEPAS to MELAB
client.request(station='MELAB')
print(client.requests)
```

If you want to make a bulk request (useful to fetch multi-station data),
you can use `request_many` method and provide a list of dictionary of
request data with argument `streams`:

```python
from richter import ArcLinkClient

client = ArcLinkClient(
    address='192.168.0.25:18001',
    user='indrarudianto.official@gmail.com',
    data_format='mseed'
)

client.request_many(streams=[
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
print(client.requests)

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

If you want to edit the request data, you can access `requests` property
and edit the data you want:

```python
# Update station channel to EHZ of the third request data
client.requests[2].update(channel='EHZ')
```


## Support

This project is maintained by Indra Rudianto. If you have any question about
this project, you can contact him at <indrarudianto.official@gmail.com>.


## License

Copyright (c) 2019 Balai Penyelidikan dan Pengembangan Teknologi Kebencanaan Geologi (BPPTKG)
