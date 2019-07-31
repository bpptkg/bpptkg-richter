"""
List poles and zeros constants of BPPTKG seismic stations.
"""

import copy

# List poles and zeros of BPPTKG seismic stations. Some stations may not be
# available, but we hope to add it in the future version.
#
# Sensitivity unit is in count/meter/sec, i.e. by inverting velocity channel
# value (meter/sec/count) on digitizer calibration sheet.
#
# Gain or A0 normalization factor is computed in rad/sec. See BPPTKG dataless
# projects on how to compute A0 normalization factor from Hz to rad/sec in
# https://gitlab.com/bpptkg/dataless/blob/master/calib/InstrumentCalibrationISOLA.pdf
#
# Poles and zeros unit are also in rad/sec, i.e. by multiplying it with 2pi.
#
# Note that this sensitivity only apply to Z channel.
PAZ = {
    # Sensitivity is 2080 according to:
    # P. Bormann: New Manual of Seismological Observatory Practice
    # IASPEI Chapter 3, page 24
    # (PITSA has 2800)
    'WOOD_ANDERSON': {
        'sensitivity': 2800,
        'gain': 1,
        'zeros': [0j],
        'poles': [
            -6.2832 - 4.7124j,
            -6.2832 + 4.7124j,
        ],
    },
    # For station MEPAS and MELAB (broadband seismometer), we obtained poles
    # and zeros values from sensor and digitizer calibration sheets document.
    # See BPPTKG dataless projects (https://gitlab.com/bpptkg/dataless)
    # Note that the sensitivity is given by 2 times (single-ended sensitivity).
    'MEPAS': {
        'sensitivity': {
            'Z': 994035785.2882704
        },
        'gain': 571507691.7712862,
        'zeros': [0j, 0j],
        'poles': [
            -0.1485973325 + 0.1485973325j,
            -0.1485973325 - 0.1485973325j,
            -1130.9733552923 + 0j,
            -1005.3096491487 + 0j,
            -502.6548245744 + 0j,
        ],
    },
    'MELAB': {
        'sensitivity': {
            'Z': 989119683.4817014
        },
        'gain': 571507691.7712862,
        'zeros': [0j, 0j],
        'poles': [
            -0.1485973325 + 0.1485973325j,
            -0.1485973325 - 0.1485973325j,
            -1130.9733552923 + 0j,
            -1005.3096491487 + 0j,
            -502.6548245744 + 0j,
        ],
    },
    # For station MEDEL and MEPUS (short period seismometer), we obtained poles
    # and zeros values from PDCC NRL tool.
    # See BPPTKG dataless projects (https://gitlab.com/bpptkg/dataless)
    'MEDEL': {
        'sensitivity': {
            'Z': 134645742.0
        },
        'gain': 1,
        'zeros': [0j, 0j],
        'poles': [
            -4.39800 + 4.48700j,
            -4.39800 - 4.48700j,
        ],
    },
    'MEPUS': {
        'sensitivity': {
            'Z': 134645742.0
        },
        'gain': 1,
        'zeros': [0j, 0j],
        'poles': [
            -4.39800 + 4.48700j,
            -4.39800 - 4.48700j,
        ],
    },
    # For station MEGRA, we obtained poles and zeros from PDCC NRL tool.
    # Note that the sensitivity is given by 2 times (single-ended sensitivity).
    'MEGRA': {
        'sensitivity': {
            'Z': 989119683.4817014
        },
        'gain': 571507691.7712862,
        'zeros': [0j, 0j],
        'poles': [
            -0.1485973325 + 0.1485973325j,
            -0.1485973325 - 0.1485973325j,
            -1130.9733552923 + 0j,
            -1005.3096491487 + 0j,
            -502.6548245744 + 0j,
        ],
    }
}


def get_paz(station, component=None):
    """Get PAZ response for certain station and component."""
    if station not in PAZ:
        raise NameError('Unknown station name {}'.format(station))

    if component:
        supported_channels = {'E', 'N', 'Z', 'e', 'n', 'z'}
        if component not in supported_channels:
            raise NameError('Unknown component name {}'.format(component))

        sensitivity = PAZ[station]['sensitivity'].get(component.upper())
        if sensitivity is None:
            raise Exception('Unsupported component {component} '
                            'on station {station}'.format(
                                component=component, station=station))

        paz = copy.deepcopy(PAZ)
        paz[station]['sensitivity'] = sensitivity
        return paz[station]
    else:
        return PAZ[station]
