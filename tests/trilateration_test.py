from pos_info.models.okomura_hata import OkomuraHata
from device_info.domain.base_station import BaseStation
from device_info.domain.user import User

import unittest

class TestTrilateration(unittest.TestCase):

    def setUp(self):
        self.model = OkomuraHata

        self.bs1 = BaseStation(identifier=0, x=0, y=0, height=30, frequency=900, power=43, gain=15)
        self.bs2 = BaseStation(identifier=1, x=100, y=0, height=30, frequency=900, power=43, gain=15)
        self.bs3 = BaseStation(identifier=2, x=50, y=80, height=30, frequency=900, power=43, gain=15)

        self.user = User(height=1.5, gain=0, bs_list=[self.bs1, self.bs2, self.bs3])
        self.user.x = 50
        self.user.y = 0
        self.user.rp_list = [-128.26606073363865, -128.26606073363865, -135.4561576848335]
    
    def test_get_path_loss_by_user_location(self):
        result = self.model.path_loss_list_by_position(self.user)
        expected = [186.26606073363865, 186.26606073363865, 193.4561576848335]
        self.assertEqual(result, expected)

    def test_get_received_power_by_user_location(self):
        expected = [-128.26606073363865, -128.26606073363865, -135.4561576848335]
        result = self.model.received_power_list_by_position(self.user)
        self.assertEqual(result, expected)

    def test_user_location_by_trilateration(self):
        result = self.user.get_position(model=self.model)
        expected = (50, 0)
        self.assertAlmostEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
