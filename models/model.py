class Model:

    @staticmethod
    def generic_path_loss(base_station, mobile_device):
        return base_station.power + base_station.gain + mobile_device.gain - mobile_device.rp_dict[base_station.identifier]

    @staticmethod
    def generic_received_power(base_station, mobile_device):
        return base_station.power + base_station.gain + mobile_device.gain - mobile_device.pl_dict[base_station.identifier]