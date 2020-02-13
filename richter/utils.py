"""
Package utility module.
"""

import os
import base64
import uuid
from dateutil import parser


def generate_safe_random_filename(extension='txt'):
    """Generate safe random filename based on UUID4."""
    name = uuid.uuid4()
    filename = base64.urlsafe_b64encode(
        name.bytes).decode('utf-8').rstrip('=\n')
    return '{filename}.{extension}'.format(
        filename=filename, extension=extension)


def to_pydatetime(*args, **kwargs):
    """
    Convert date string to Python datetime.
    """
    date_obj = parser.parse(*args, **kwargs)
    return date_obj


def find_executable(executable, path=None):
    """Find full path executable command."""

    if path is None:
        path = os.environ['PATH']

    paths = path.split(os.pathsep)

    for name in paths:
        filename = os.path.join(name, executable)
        if os.path.isfile(filename):
            return filename
    return None


def stringify_parameters(items):
    """
    Convert all items in list to string.
    """
    return [str(item) for item in items]
