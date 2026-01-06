import unittest
from pos_info.models.okomura_hata import OkomuraHata
from device_info.domain.user import User
from device_info.domain.base_station import BaseStation


class TestOkomuraHata(unittest.TestCase):

    def setUp(self):
        self.bs1 = BaseStation(identifier=0, x=0, y=0, height=40, frequency=900, power=43, gain=15)
        self.bs2 = BaseStation(identifier=1, x=1000, y=0, height=30, frequency=900, power=43, gain=15)
        self.bs3 = BaseStation(identifier=2, x=500, y=866, height=50, frequency=900, power=43, gain=15)

        self.user = User(height=1.5, gain=0, bs_list=[self.bs1, self.bs2, self.bs3])
        self.user.x, self.user.y = 100, 200
        self.user.rp_list = {0: -75, 1: -33.18, 2: -85}
        self.user.pl_list = {0: 120, 1: 125, 2: 130}

        self.model = OkomuraHata

    def test_correction_factor_big_city(self):
        result = self.model.correction_factor(md_height=1.5, frequency=900, big_city=True)
        expected = -0.00092
        self.assertAlmostEqual(result, expected, places=5)

    def test_correction_factor_small_city(self):
        result = self.model.correction_factor(md_height=1.5, frequency=900, big_city=False)
        expected = 0.01588
        self.assertAlmostEqual(result, expected, places=5)

    def test_path_loss(self):
        distance = 0.1
        expected = 91.18 
        result = self.model.path_loss(self.bs2, self.user, True, distance)
        self.assertAlmostEqual(result, expected, places=1)

    def test_distance(self):
        result = self.model.distance(self.bs2, self.user, True)
        expected = 0.1
        self.assertAlmostEqual(result, expected, places=3)

    def test_received_power_list_by_position(self):
        self.bs1 = BaseStation(identifier=0, x=0, y=0, height=30, frequency=900, power=43, gain=15)
        self.bs2 = BaseStation(identifier=1, x=100, y=0, height=30, frequency=900, power=43, gain=15)
        self.bs3 = BaseStation(identifier=2, x=50, y=80, height=30, frequency=900, power=43, gain=15)
        self.user = User(height=1.5, gain=0, bs_list=[self.bs1, self.bs2, self.bs3])
        self.user.x = 50
        self.user.y = 0
        self.user.rp_list = []
        result = self.model.received_power_list_by_position(md=self.user)
        expected = [-128.26606073363865, -128.26606073363865, -135.4561576848335]
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
