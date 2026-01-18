import math
from models.model import Model

class OkomuraHata(Model):

    
    #distance: km
    #frequency: MHz
    #height: m
    #path loss: dBm

    def correction_factor( md_height, frequency, big_city):
        if big_city:
            return 3.2 * (math.log10(11.75 * md_height))**2 - 4.97
        else:
            return (1.1 * math.log10(frequency) - 0.7) * md_height - (1.56 * math.log10(frequency) - 0.8)

    def path_loss(base_station, mobile_device, is_bigcity, input_distance=None):
        if input_distance == None:
            distance = math.hypot(
                base_station.x - mobile_device.x, 
                base_station.y - mobile_device.y)
        else:
            distance = input_distance
        correction_factor = OkomuraHata.correction_factor(mobile_device.height, base_station.frequency, is_bigcity)
        path_loss = (69.55 + 26.16 * math.log10(base_station.frequency)
            - 13.82 * math.log10(base_station.height)
            - correction_factor
            + (44.9 - 6.55 * math.log10(base_station.height)) * math.log10(distance))
        return path_loss

    @staticmethod
    def received_power(base_station, mobile_device, is_bigcity, input_distance=None):
        if input_distance is None:
            distance = math.hypot(
                base_station.x - mobile_device.x, 
                base_station.y - mobile_device.y)
        else:
            distance = input_distance
        path_loss = OkomuraHata.path_loss(base_station, mobile_device, is_bigcity, distance)
        mobile_device.pl_list[base_station.identifier] = path_loss
        received_power = Model.generic_received_power(base_station, mobile_device)
        return received_power   
    
    @staticmethod
    def distance(base_station, mobile_device, is_bigcity):
        path_loss = Model.generic_path_loss(base_station, mobile_device)
        correcetion_factor = OkomuraHata.correction_factor(mobile_device.height, base_station.frequency, is_bigcity)
        K = 44.9 - 6.55 * math.log10(base_station.height)
        log_distance = (path_loss - (69.55 + 26.16 * math.log10(base_station.frequency) - 13.82 * math.log10(base_station.height) - correcetion_factor)) / K
        distance = 10 ** log_distance
        return distance
    
    def path_loss_list_by_position( md):
        pl_list = [None] * 3
        for index, bs in enumerate(md.bs_list):
            distance = math.hypot(bs.x - md.x, bs.y - md.y)
            pl_list[index] = OkomuraHata.path_loss(base_station=bs, mobile_device=md, is_bigcity=True, input_distance=distance)
        md.pl_list = pl_list
        return pl_list
     
    def received_power_list_by_position(md):
        if len(md.pl_list) < len(md.bs_list):
            OkomuraHata.path_loss_list_by_position(md)
        rp_list = [None] * 3
        for index, bs in enumerate(md.bs_list):
            rp_list[index] = Model.generic_received_power(bs, md)
        md.rp_list = rp_list
        return rp_list
        