"""
SeedLink and ArcLink client wrapper.
"""

import os
import sys
import tempfile
import subprocess

from . import utils


class LinkError(Exception):
    """Base link client wrapper error exception."""
    pass


def build_request_file(starttime, endtime, station, network='VG', channel='HHZ',
                       location='00', request_file=None):
    """
    Build ArcLink request file.

    The request file format has the following format:

    YYYY,MM,DD,HH,MM,SS YYYY,MM,DD,HH,MM,SS Network Station Channel [Location]

    the Channel, Station and Location, can contains wildcards (*) and the
    Location field is optional although we explicitly define it in the request
    file. For matching all locations you can use the '*' symbol, if empty it
    assumes that only empty locations are being requested.

    Example:

    2010,02,18,12,00,00 2010,02,18,12,10,00 GE WLF BH*
    2010,02,18,12,00,00 2010,02,18,12,10,00 GE VSU BH* 00

    Note that starttime and endtime for request are in UTC timezone. For more
    information, see the following ArcLink CLI client documentation at
    https://www.seiscomp3.org/doc/jakarta/current/apps/arclink_fetch.html
    """
    date_format = '%Y,%m,%d,%H,%M,%S'
    if not request_file:
        filename = utils.generate_safe_random_filename()
        path = os.path.join(tempfile.gettempdir(), filename)
    else:
        path = request_file

    start = utils.to_pydatetime(starttime) if isinstance(
        starttime, str) else starttime
    end = utils.to_pydatetime(endtime) if isinstance(endtime, str) else endtime

    with open(path, 'w') as buf:
        buf.write(
            '{starttime} {endtime} {network} {station} {channel} {location}'.format(
                starttime=start.strftime(date_format),
                endtime=end.strftime(date_format),
                network=network,
                station=station,
                channel=channel,
                location=location
            ))
    return path


class ArcLinkClient(object):
    """ArcLink client wrapper."""

    accepts_parameters = {
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
    required_parameters = ['address', 'user']
    arclink_cli = 'arclink_fetch'
    python_cmd = '/usr/bin/python'

    def __init__(self, **kwargs):
        for key, value in self.accepts_parameters.items():
            if key in kwargs:
                new_value = kwargs[key]
            else:
                new_value = value
            setattr(self, key, new_value)
        self.request_file = kwargs.pop('request_file', None)
        self.output_path = kwargs.pop('output_path', None)

    def _check_required(self):
        for name in self.required_parameters:
            if not getattr(self, name):
                raise LinkError('Parameter {} is required'.format(name))

        if not os.path.isfile(self.python_cmd):
            self.python_cmd = utils.find_executable('python')
            assert sys.version_info < (3, 0), (
                'Python version 2.x is required to run arclink_fetch. '
                'Make sure you have Python version 2.x installed. '
                'Default Python executable is in /usr/bin/python.'
            )

    def _build_cli(self):
        arclink_cmd = utils.find_executable(self.arclink_cli)
        if arclink_cmd is None:
            raise LinkError('Could not find arclink_fetch executable')
        return [self.python_cmd, arclink_cmd]

    def _build_cli_arguments(self):
        if not self.request_file:
            raise LinkError('Request file is not built yet')

        args = []
        underscore = '_'
        dash = '-'
        for name in self.accepts_parameters:
            value = getattr(self, name)
            if value:
                if isinstance(value, bool):
                    arg_format = '--{name}'
                else:
                    arg_format = '--{name}={value}'

                args.append(arg_format.format(
                    name=name.replace(underscore, dash), value=value))
        return args + [self.request_file]

    def _build_cli_with_args(self):
        return self._build_cli() + self._build_cli_arguments()

    def request(self, *args, **kwargs):
        """
        Prepare ArcLink request.

        It builds the request file and generate random output file it if not
        explicitly set by user. Positional arguments required are starttime,
        endtime, and station name.
        """
        self.request_file = build_request_file(*args, **kwargs)
        output_file = utils.generate_safe_random_filename(
            self.data_format)

        if self.output_path is None:
            self.output_path = tempfile.gettempdir()
        self.output_file = os.path.join(self.output_path, output_file)

    def execute(self, **kwargs):
        """Execute ArcLink request."""
        self._check_required()

        cli_with_args = self._build_cli_with_args()
        completed_process = subprocess.run(cli_with_args, **kwargs)
        return completed_process


class SeedLinkClient(object):
    """SeedLink client wrapper."""
    pass
