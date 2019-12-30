import unittest

from richter import ml


class SeismicEnergyTest(unittest.TestCase):

    def test_compute_seismic_energy(self):
        self.assertAlmostEqual(
            10**(12.8), ml.compute_seismic_energy(2.0/3.0), delta=1e-3)


if __name__ == '__main__':
    unittest.main()
