# bpptkg-richter

![](https://github.com/bpptkg/bpptkg-richter/workflows/Build/badge.svg)

**bpptkg-richter** is a Python library for computing Richter local magnitude
scales on BPPTKG seismic network.

## Installation

Install using pip:

    pip install -U bpptkg-richter

## Richter Magnitude Scales

You may want to install [ObsPy](https://www.obspy.org/) package, because this
package only work on ObsPy stream type. Default network is `VG` and default
component is `Z`:

```python
from obspy import read
import richter

# Read single station or multiple stations streams
stream = read('/path/to/stream.mseed')

# Compute Richter local magnitude for station MEPAS
ml = richter.compute_ml(stream, 'MEPAS', network='VG', component='Z')

# Compute Wood-Anderson zero-to-peak amplitude in meter for station MEPAS
wa_ampl = richter.compute_wa(stream, 'MEPAS', network='VG', component='Z')

# Compute count amplitude peak-to-peak for station MEPAS
app = richter.compute_app(stream, 'MEPAS', network='VG', component='Z')
```

or for short:

```python
from obspy import read
import richter

stream = read('/path/to/stream.mseed')

ml = richter.compute_ml(stream, 'MEPAS')
wa_ampl = richter.compute_wa(stream, 'MEPAS')
app = richter.compute_app(stream, 'MEPAS')
```

For current version, on computing local magnitude (`compute_ml`) and
Wood-Anderson amplitude(`compute_wa`), the only supported component is `Z`
component.

`compute_app` support other components, for example:

```python
app = richter.compute_app(stream, 'MELAB', component='E')
```

## Documentation

Full documentation and guides are available at `docs/` directory and online at
https://bpptkg-richter.readthedocs.io/en/latest/.

## License

By contributing to the project, you agree that your contributions will be
licensed under its MIT license. See
[LICENSE](https://github.com/bpptkg/bpptkg-richter/blob/master/LICENSE) for
details.
