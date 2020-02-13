"""
SeedLink and ArcLink client wrapper.
"""

import os
import sys
import datetime
import tempfile
import subprocess
from contextlib import contextmanager

from . import utils

__all__ = [
    'build_request_file',
    'ArcLinkClient',
    'SeedLinkClient',
    'stream_manager',
]


class LinkError(Exception):
    """Base link client wrapper error exception."""
    pass


def build_request_file(starttime, endtime, network, station, channel,
                       location='00', request_file=None, mode='a'):
    """
    Build ArcLink request file.

    The request file format has the following format: ::

        YYYY,MM,DD,HH,MM,SS YYYY,MM,DD,HH,MM,SS Network Station Channel [Location]

    the Channel, Station and Location, can contains wildcards (*) and the
    Location field is optional although we explicitly define it in the request
    file. For matching all locations you can use the '*' symbol, if empty it
    assumes that only empty locations are being requested.

    Example: ::

        2010,02,18,12,00,00 2010,02,18,12,10,00 GE WLF BH*
        2010,02,18,12,00,00 2010,02,18,12,10,00 GE VSU BH* 00

    Note that starttime and endtime for request are in UTC timezone. For more
    information, see the following ArcLink CLI client documentation at
    https://www.seiscomp3.org/doc/jakarta/current/apps/arclink_fetch.html.
    """
    date_format = '%Y,%m,%d,%H,%M,%S'
    if not request_file:
        filename = utils.generate_safe_random_filename()
        path = os.path.join(tempfile.gettempdir(), filename)
    else:
        path = request_file

    if isinstance(starttime, str):
        start = utils.to_pydatetime(starttime)
    elif isinstance(starttime, datetime.datetime):
        start = starttime
    else:
        raise LinkError('Unsupported starttime format')

    if isinstance(endtime, str):
        end = utils.to_pydatetime(endtime)
    elif isinstance(endtime, datetime.datetime):
        end = endtime
    else:
        raise LinkError('Unsupported endtime format')

    if isinstance(channel, (list, tuple)):
        channels = channel
    elif isinstance(channel, str):
        channels = [channel]
    else:
        raise LinkError(
            'Stream channel does not support {} type'.format(type(channel)))

    with open(path, mode) as buf:
        for sta_channel in channels:
            buf.write(
                '{starttime} {endtime} {network} '
                '{station} {channel} {location}\n'.format(
                    starttime=start.strftime(date_format),
                    endtime=end.strftime(date_format),
                    network=network,
                    station=station,
                    channel=sta_channel,
                    location=location
                ))
    return path


class ArcLinkClient(object):
    """
    ArcLink client wrapper.

    This client wrap arclink_fetch command to request time window-based data
    over ArcLink. It supports single station or multi-stations request.

    Note that arclink_fetch only run on Python 2.x. This client use default
    Python 2.x executable at /usr/bin/python to run arclink_fetch command.
    See arclink_fetch documentation at the following link:
    https://www.seiscomp3.org/doc/applications/arclink_fetch.html
    """

    name = 'arclink'
    default_parameters = {
        'address': None,
        'request_format': 'native',
        'data_format': 'mseed',
        'preferred_sample_rate': None,
        'label': None,
        'no_resp_dict': False,
        'rebuild_volume': False,
        'proxy': False,
        'timeout': 300,
        'retries': 5,
        'user': None,
        'output_file': None
    }
    arclink_cli = 'arclink_fetch'
    python_cmd = '/usr/bin/python'

    def __init__(self, **kwargs):
        for key, value in self.default_parameters.items():
            if key in kwargs:
                new_value = kwargs[key]
            else:
                new_value = value
            setattr(self, key, new_value)
        self.request_file = kwargs.pop('request_file', None)
        self.output_path = kwargs.pop('output_path', None)
        self.request_data = []

    def _check_required(self):
        required_parameters = ['address', 'user']
        for name in required_parameters:
            if not getattr(self, name):
                raise LinkError('Parameter {} is required'.format(name))

        if not os.path.isfile(self.python_cmd):
            self.python_cmd = utils.find_executable('python')
            assert sys.version_info < (3, 0), (
                'Python version 2.x is required to run arclink_fetch. '
                'Make sure you have Python version 2.x installed. '
                'Default Python executable is in /usr/bin/python.'
            )

    def _check_request_parameters(self, item):
        required_request_parameters = [
            'starttime', 'endtime', 'network', 'station', 'channel']
        for name in required_request_parameters:
            if item.get(name) is None:
                raise LinkError(
                    'Request parameter {} is required'.format(name))

    def _build_request_file(self):
        if os.path.exists(self.request_file):
            os.unlink(self.request_file)

        for request in self.request_data:
            self._check_request_parameters(request)

            build_request_file(
                request['starttime'],
                request['endtime'],
                request['network'],
                request['station'],
                request['channel'],
                location=request.get('location', '00'),
                request_file=self.request_file,
                mode='a')

    def _build_cli(self):
        arclink_cmd = utils.find_executable(self.arclink_cli)
        if arclink_cmd is None:
            raise LinkError('Could not find arclink_fetch executable')
        return [self.python_cmd, arclink_cmd]

    def _build_cli_arguments(self):
        if self.output_path is None:
            self.output_path = tempfile.gettempdir()
        if self.request_file is None:
            self.request_file = os.path.join(
                self.output_path,
                utils.generate_safe_random_filename())
        output_file = utils.generate_safe_random_filename(
            self.data_format)
        if self.output_file is None:
            self.output_file = os.path.join(self.output_path, output_file)

        args = []
        underscore = '_'
        dash = '-'
        for name in self.default_parameters:
            value = getattr(self, name)
            if value:
                if isinstance(value, bool):
                    arg_format = '--{name}'
                else:
                    arg_format = '--{name}={value}'

                args.append(arg_format.format(
                    name=name.replace(underscore, dash), value=value))
        return args + [self.request_file]

    def _build_cli_with_arguments(self):
        return self._build_cli() + self._build_cli_arguments()

    def request(self, **kwargs):
        """
        Prepare ArcLink single station request.
        """
        if not self.request_data:
            self.request_data.append({})
        self.request_data[0].update(kwargs)

    def request_many(self, stream_list=None, **kwargs):
        """
        Prepare ArcLink many station request.
        """
        if stream_list:
            if isinstance(stream_list, (list, tuple)):
                self.request_data = list(stream_list)
            elif isinstance(stream_list, dict):
                self.request_data.append(stream_list)
        else:
            self.request_data.append(kwargs)

    def clear_request(self):
        """Clear all ArcLink request data."""
        self.request_data.clear()

    def execute(self, **kwargs):
        """Execute ArcLink request."""
        self._check_required()
        cli_with_args = self._build_cli_with_arguments()
        safe_cli_with_args = utils.stringify_parameters(cli_with_args)

        self._build_request_file()
        if sys.version_info < (3, 5):
            completed_process = subprocess.call(safe_cli_with_args, **kwargs)
        else:
            completed_process = subprocess.run(safe_cli_with_args, **kwargs)
        return completed_process


class SeedLinkClient(object):
    """
    SeedLink client wrapper.

    This client is not intended to record data by realtime, but to request
    time window-based data over SeedLink. If you intend to record realtime
    data over SeedLink, probably you want to use executable slinktool directly.
    This client only wrap minimal options of slinktool program. See slinktool
    documentation at the following link:
    https://www.seiscomp3.org/doc/applications/slinktool.html
    """

    name = 'seedlink'
    default_parameters = {
        'address': None,
        'delay': 30,
        'timeout': 60,
        'data_format': 'mseed',
        'stream_list': None,
        'time_window': None,
        'output_file': None,
        'output_path': None,
    }
    seedlink_cli = 'slinktool'

    def __init__(self, **kwargs):
        for key, value in self.default_parameters.items():
            if key in kwargs:
                new_value = kwargs[key]
            else:
                new_value = value
            setattr(self, key, new_value)

        self.request_data = {'streams': [], 'starttime': None, 'endtime': None}

    def _check_required(self):
        required_parameters = ['stream_list', 'time_window']
        for name in required_parameters:
            if not getattr(self, name):
                raise LinkError('Parameter {} is required'.format(name))

    def _check_request_parameters(self):
        if self.request_data['starttime'] is None:
            raise LinkError('Parameter starttime is required')
        if self.request_data['endtime'] is None:
            raise LinkError('Parameter endtime is required')

    def _check_netsta(self, item):
        required_request_parameters = ['network', 'station']
        for name in required_request_parameters:
            if not item.get(name):
                raise LinkError(
                    'Request parameter {} is required'.format(name))

    def _build_stream_list(self):
        streams = []
        selector_template = ':{channel}'
        for stream in self.request_data['streams']:
            self._check_netsta(stream)

            network = stream.get('network')
            station = stream.get('station')
            channel = stream.get('channel')
            netsta = '{network}_{station}'.format(
                network=network, station=station)

            if isinstance(channel, (list, tuple)):
                selector = selector_template.format(
                    channel=' '.join(map(str, channel)))
            elif isinstance(channel, str):
                selector = selector_template.format(channel=channel)
            else:
                selector = ''
            streams.append(netsta + selector)
        return ','.join(map(str, streams))

    def _build_time_window(self):
        starttime = self.request_data['starttime']
        endtime = self.request_data['endtime']

        if isinstance(starttime, str):
            start = utils.to_pydatetime(starttime)
        elif isinstance(starttime, datetime.datetime):
            start = starttime
        else:
            raise LinkError('Unsupported starttime format')

        if isinstance(endtime, str):
            end = utils.to_pydatetime(endtime)
        elif isinstance(endtime, datetime.datetime):
            end = endtime
        else:
            raise LinkError('Unsupported endtime format')

        date_format = r'%Y,%m,%d,%H,%M,%S'
        time_window = '{starttime}:{endtime}'.format(
            starttime=start.strftime(date_format),
            endtime=end.strftime(date_format) if end else ''
        )
        return time_window

    def _build_cli(self):
        seedlink_cmd = utils.find_executable(self.seedlink_cli)
        if seedlink_cmd is None:
            raise LinkError('Could not find slinktool executable')
        return [seedlink_cmd]

    def _build_cli_arguments(self):
        if self.time_window is None:
            self.time_window = self._build_time_window()
        if self.stream_list is None:
            self.stream_list = self._build_stream_list()
        if self.output_path is None:
            self.output_path = tempfile.gettempdir()
        if self.output_file is None:
            output_file = utils.generate_safe_random_filename(self.data_format)
            self.output_file = os.path.join(self.output_path, output_file)
        return [
            '-nd', self.delay,
            '-nt', self.timeout,
            '-tw', self.time_window,
            '-S', self.stream_list,
            '-o', self.output_file,
            self.address,
        ]

    def _build_cli_with_arguments(self):
        return self._build_cli() + self._build_cli_arguments()

    def request(self, **kwargs):
        """
        Prepare SeedLink single station request.
        """
        if not self.request_data['streams']:
            self.request_data['streams'].append({})

        self.request_data['starttime'] = kwargs.pop(
            'starttime', self.request_data['starttime'])
        self.request_data['endtime'] = kwargs.pop(
            'endtime', self.request_data['endtime'])

        self.request_data['streams'][0].update(kwargs)

    def request_many(self, stream_list=None, **kwargs):
        """
        Prepare SeedLink many stations request.
        """
        self.request_data['starttime'] = kwargs.pop(
            'starttime', self.request_data['starttime'])
        self.request_data['endtime'] = kwargs.pop(
            'endtime', self.request_data['endtime'])

        if stream_list:
            if isinstance(stream_list, (list, tuple)):
                self.request_data['streams'] = list(stream_list)
            elif isinstance(stream_list, dict):
                self.request_data['streams'].append(stream_list)
        else:
            self.request_data['streams'].append(kwargs)

    def clear_request(self):
        """Clear all SeedLink request data."""
        self.request_data = {'streams': [], 'starttime': None, 'endtime': None}

    def execute(self, **kwargs):
        """Execute SeedLink request."""
        self._check_request_parameters()
        cli_with_args = self._build_cli_with_arguments()
        self._check_required()

        safe_cli_with_args = utils.stringify_parameters(cli_with_args)

        if sys.version_info < (3, 5):
            completed_process = subprocess.call(safe_cli_with_args, **kwargs)
        else:
            completed_process = subprocess.run(safe_cli_with_args, **kwargs)
        return completed_process


@contextmanager
def stream_manager(**kwargs):
    """
    Context manager of ArcLinkClient class.

    It yields stream file path if request succeed, and remove request file
    and stream file on exit.

    Example:

    .. code-block:: python

        from obspy import read
        from richter import stream_manager

        with stream_manager(address='192.168.0.25:18001',
                            starttime='2019-01-01 00:00:00',
                            endtime='2019-01-01 01:00:00',
                            network='VG',
                            station='MEPAS',
                            channel='HHZ') as stream_file:
            stream = read(stream_file)
            # Then, do something with stream.
    """
    address = kwargs.pop('address', None)
    if address is None:
        raise LinkError('Parameter address is required')

    client = ArcLinkClient(address=address,
                           user='user',
                           data_format='mseed')
    client.request_many(**kwargs)

    try:
        client.execute()
        yield client.output_file
    finally:
        if os.path.exists(client.output_file):
            os.unlink(client.output_file)
        if os.path.exists(client.request_file):
            os.unlink(client.request_file)
