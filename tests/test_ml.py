import unittest

from richter import ml


class SeismicEnergyTest(unittest.TestCase):

    def test_compute_seismic_energy(self):
        self.assertAlmostEqual(
            10**(12.8)/10**12, ml.compute_seismic_energy(2.0/3.0), delta=1e-3)

    def test_compute_analog_ml(self):
        self.assertAlmostEqual(
            ml.compute_analog_ml(10),
            1.30288852558,
            delta=1e-3
        )

        self.assertAlmostEqual(
            ml.compute_analog_ml(50),
            2.00185852991,
            delta=1e-3
        )

        self.assertAlmostEqual(
            ml.compute_analog_ml(113),
            2.35596696906,
            delta=1e-3
        )


if __name__ == '__main__':
    unittest.main()
