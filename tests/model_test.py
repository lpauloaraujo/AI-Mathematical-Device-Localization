import unittest
from pos_info.models.model import Model
from device_info.domain.base_station import BaseStation
from device_info.domain.user import User

class TestModel(unittest.TestCase):
    def setUp(self):
        self.bs1 = BaseStation(identifier=0, x=0, y=0, height=30, frequency=900, power=40, gain=15)
        self.bs2 = BaseStation(identifier=1, x=100, y=0, height=35, frequency=1800, power=35, gain=10)
        self.bs3 = BaseStation(identifier=2, x=50, y=100, height=25, frequency=2100, power=30, gain=8)
        self.bs4 = BaseStation(identifier=3, x=10000, y=5100, height=32, frequency=2100, power=30, gain=10)
        self.bs_list = [self.bs1, self.bs2, self.bs3, self.bs4]

        self.user = User(
            height=1.5,
            gain=5,
            bs_list=self.bs_list
        )

#    def test_generic_path_loss_bs1(self):
#        expected = 40 + 15 + 5 - 90  # = -30
#        result = Model.generic_path_loss(self.bs1, self.user)
#        self.assertEqual(result, expected)

#    def test_generic_path_loss_bs2(self):
#        expected = 35 + 10 + 5 - 100  # = -50
#        result = Model.generic_path_loss(self.bs2, self.user)
#        self.assertEqual(result, expected)

#    def test_generic_received_power_bs3(self):
#        expected = 30 + 8 + 5 - 105  # = -62
#        result = Model.generic_received_power(self.bs3, self.user)
#        self.assertEqual(result, expected)

#    def test_different_user_gain(self):
#        self.user.gain = 0
#        expected = 40 + 15 + 0 - 90  # = -35
#        result = Model.generic_path_loss(self.bs1, self.user)
#        self.assertEqual(result, expected)

#    def test_get_neighbours(self):
#        bs_list = self.user.bs_list
#        for bs in bs_list:
#            bs.get_neighbours(bs_list)
#       self.assertEqual(self.bs1.neigh_bs, [self.bs1, self.bs2, self.bs3])

if __name__ == '__main__':
    unittest.main()
