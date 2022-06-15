"""
Utility module for computing Richter magnitude scales, i.e. ML or local
magnitude on BPPTKG seismic network.
"""

import numpy as np
from . import paz


def filter_stream(stream, **kwargs):
    """
    Filter ObsPy stream object.

    :param stream: ObsPy waveform stream object.
    :type stream: :class:`obspy.core.stream.Stream`

    Example:

    .. code-block:: python

        from richter import filter_stream
        from obspy import read

        stream = read('/path/to/stream.msd')
        print(stream)

        filtered_stream = filter_stream(
            stream, network='VG', station='MEPAS', component='Z')
        print(filtered_stream)

    """
    filtered_stream = stream.copy().select(**kwargs)
    if filtered_stream.count() > 1:
        filtered_stream.merge(method=1, fill_value="interpolate")
    return filtered_stream


def compute_bpptkg_ml(wa_ampl):
    """
    Compute BPPTKG Richter magnitude scales using Wood-Anderson amplitude.

    Note that Wood Anderson zero to peak amplitude (wa_ampl) is in mm.
    Calibration function log10(A0) for BPPTKG seismic network is -1.4.

    :param wa_ampl: Wood-Anderson zero to peak amplitude in mili-meter.
    :type wa_ampl: float
    :return: BPPTKG Richter magnitude scale.
    :rtype: float

    Richter magnitude scale is computed using the following equation: ::

        ml = log10(wa_ampl) - log10(A0)

    where log10(A0) equal to -1.4 and ml is Richter local magnitude scale.

    Example:

    .. code-block:: python

        from richter import compute_bpptkg_ml

        # Wood Anderson zero to peak amplitude in mm
        wa_ampl = 5

        ml = compute_bpptkg_ml(wa_ampl)
        print(ml)

    """
    return np.log10(wa_ampl) + 1.4


def compute_wa(stream, station, network="VG", component="Z", **kwargs):
    """
    Compute stream Wood-Anderson amplitude in meter.

    :param stream: ObsPy waveform stream object.
    :type stream: :class:`obspy.core.stream.Stream`
    :param station: Seismic station name, e.g. MEPAS, MEGRA, etc.
    :type station: str
    :param network: Seismic network name, default to VG.
    :type network: str
    :param component: Seismic station component, e.g E, N, Z, default to Z.
    :type component: str
    :return: Wood-Anderson zero to peak amplitude in meter.
    :rtype: float

    Exampe:

    .. code-block:: python

        from richter import compute_wa
        from obspy import read

        stream = read('/path/to/stream.msd')
        wa_ampl = compute_wa(stream, 'MEPAS', component='Z')
        print(wa_ampl)

    """
    filtered_stream = filter_stream(
        stream, station=station, network=network, component=component, **kwargs
    )
    if not filtered_stream:
        return None
    filtered_stream.simulate(
        paz_remove=paz.get_paz(station, component),
        paz_simulate=paz.PAZ["WOOD_ANDERSON"],
        water_level=0.0,
    )
    wa_ampl = np.max(np.abs(filtered_stream[0].data))
    return wa_ampl


def compute_ml(stream, station, network="VG", component="Z", **kwargs):
    """
    Compute Richter magnitude scales.

    :param stream: ObsPy waveform stream object.
    :type stream: :class:`obspy.core.stream.Stream`
    :param station: Seismic station name, e.g. MEPAS, MEGRA, etc.
    :type station: str
    :param network: Seismic network name, default to VG.
    :type network: str
    :param component: Seismic station component, e.g E, N, Z, default to Z.
    :type component: str
    :return: BPPTKG Richter magnitude scale.
    :rtype: float

    Example:

    .. code-block:: python

        from richter import compute_ml
        from obspy import read

        stream = read('/path/to/stream.msd')
        ml = compute_ml(stream, 'MEPAS', component='Z')
        print(ml)

    """
    wa_ampl = compute_wa(
        stream, station, network=network, component=component, **kwargs
    )
    if not wa_ampl:
        return None
    # Convert WA amplitude from meter to mili-meter
    richter_ml = compute_bpptkg_ml(wa_ampl * 1000)
    return richter_ml


def compute_analog_ml(p2p_amplitude):
    """
    Compute Richter magnitude scales from seismic analog peak-to-peak amplitude.

    The peak-to-peak value must be obtained from DEL (Deles) analog station and
    in mm unit.

    :param p2p_amplitude: Peak-to-peak amplitude in mm unit.
    :type p2p_amplitude: float
    :return: BPPTKG Richter magnitude scale.
    :rtype: float

    Example:

    .. code-block:: python

        from richter import compute_analog_ml

        p2p_amplitude = 50
        ml = compute_analog_ml(p2p_amplitude)
        print(ml)

    """
    # k1, k2, and k3 is correction factors that map DEL amplitude scale to PUS
    # amplitude scale.
    k1 = 2800 / (0.13 * 27000)
    k2 = 20.0 / 50.0
    k3 = 3981.0 / 7943.0
    ampl = p2p_amplitude / 2.0
    return compute_bpptkg_ml(k1 * k2 * k3 * ampl)


def compute_app(stream, station, network="VG", component="Z", **kwargs):
    """
    Compute stream amplitude peak to peak.

    :param stream: ObsPy waveform stream object.
    :type stream: :class:`obspy.core.stream.Stream`
    :param station: Seismic station name, e.g. MEPAS, MEGRA, etc.
    :type station: str
    :param network: Seismic network name, default to VG.
    :type network: str
    :param component: Seismic station component, e.g E, N, Z, default to Z.
    :type component: str
    :return: Stream amplitude peak to peak.
    :rtype: int

    Example:

    .. code-block:: python

        from richter import compute_app
        from obspy import stream

        stream = read('/path/to/stream.msd')
        app = compute_app(stream, 'MEPAS', component='Z')
        print(app)

    """
    filtered_stream = filter_stream(
        stream, station=station, network=network, component=component, **kwargs
    )
    if not filtered_stream:
        return None
    app = np.abs(np.min(filtered_stream[0].data)) + np.abs(
        np.max(filtered_stream[0].data)
    )
    return app


def compute_seismic_energy(m):
    """
    Compute seismic energy using Gutenberg-Richter equation.

    .. math::

        log E = 11.8 + 1.5M

    where :math:`M` is Richter local magnitude  and :math:`E` is energy in ergs.

    :param m: Richter local magnitude.
    :type m: float
    :return: Seismic energy in factor of :math:`10^{12}` ergs.
    :rtype: float

    Example:

    .. code-block:: python

        from richter import compute_seismic_energy

        ml = 1.5
        energy = compute_seismic_energy(ml)
        print(energy)

    """
    return 10 ** (11.8 + 1.5 * m) / 10**12


def compute_seismic_energy_from_stream(
    stream, station, network="VG", component="Z", **kwargs
):
    """
    Compute seismic energy using Gutenberg-Richter equation using stream as
    input.

    Seismic energy is computed using the following equation:

    .. math::

        log E = 11.8 + 1.5M

    where :math:`M` is Richter local magnitude  and :math:`E` is energy in ergs.

    :param stream: ObsPy waveform stream object.
    :type stream: :class:`obspy.core.stream.Stream`
    :param station: Seismic station name, e.g. MEPAS, MEGRA, etc.
    :type station: str
    :param network: Seismic network name, default to VG.
    :type network: str
    :param component: Seismic station component, e.g E, N, Z, default to Z.
    :type component: str
    :return: Seismic energy in factor of :math:`10^{12}` ergs.
    :rtype: float

    Example:

    .. code-block:: python

        from richter import compute_seismic_energy_from_stream
        from obspy import read

        stream = read('/path/to/stream.msd')
        energy = compute_energy_from_stream(stream, 'MEPAS', component='Z')
        print(energy)

    """
    ml = compute_ml(stream, station, network=network, component=component, **kwargs)
    if ml is None:
        return None
    return compute_seismic_energy(ml)
