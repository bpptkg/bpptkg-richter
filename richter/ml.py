"""
Utility module for computing Richter magnitude scales, i.e. ML or local
magnitude on BPPTKG seismic network.
"""

import numpy as np
from . import paz

__all__ = [
    'filter_stream',
    'compute_bpptkg_ml',
    'compute_wa',
    'compute_ml',
    'compute_app',
]


def filter_stream(stream, **kwargs):
    """Filter ObsPy stream object."""
    filtered_stream = stream.copy().select(**kwargs)
    if filtered_stream.count() > 1:
        filtered_stream.merge(method=1)
    return filtered_stream


def compute_bpptkg_ml(wa_ampl):
    """
    Compute BPPTKG Richter magnitude scales using Wood-Anderson amplitude.

    Note that Wood Anderson zero to peak amplitude (wa_ampl) is in mm.
    Calibration function log10(A0) for BPPTKG seismic network is 1.4.
    """
    return np.log10(wa_ampl) + 1.4


def compute_wa(stream, station, network='VG', component='Z', **kwargs):
    """Compute stream Wood-Anderson amplitude in meter."""
    filtered_stream = filter_stream(stream, station=station, network=network,
                                    component=component, **kwargs)
    if not filtered_stream:
        return None
    filtered_stream.simulate(paz_remove=paz.get_paz(station, component),
                             paz_simulate=paz.PAZ['WOOD_ANDERSON'],
                             water_level=0.0)
    wa_ampl = np.max(np.abs(filtered_stream[0].data))
    return wa_ampl


def compute_ml(stream, station, network='VG', component='Z', **kwargs):
    """Compute Richter magnitude scales."""
    wa_ampl = compute_wa(stream, station, network=network,
                         component=component, **kwargs)
    if not wa_ampl:
        return None
    # Convert WA amplitude from meter to mili-meter
    richter_ml = compute_bpptkg_ml(wa_ampl * 1000)
    return richter_ml


def compute_app(stream, station, network='VG', component='Z', **kwargs):
    """Compute stream amplitude peak to peak."""
    filtered_stream = filter_stream(stream, station=station, network=network,
                                    component=component, **kwargs)
    if not filtered_stream:
        return None
    app = np.abs(np.min(filtered_stream[0].data)) + \
        np.abs(np.max(filtered_stream[0].data))
    return app
