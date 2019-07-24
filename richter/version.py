"""
Package version module.
"""

__version__ = '0.1.0'


def get_version():
    """Get package version string."""
    return __version__


def get_version_as_tuple():
    """Get package version as tuple."""
    return tuple(map(int, __version__.split('.')))
