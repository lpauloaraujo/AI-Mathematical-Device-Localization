import json
from domain.base_station import BaseStation
from domain.user import User

def jsonmap(object, path):
    if object.lower() == "bs":

        with open(path) as f:
            bs_data_list = json.load(f)

        return [BaseStation.from_dict(bs_data) for bs, bs_data in bs_data_list.items()]
    
    if object.lower() == "user":
        
        with open(path) as f:
            user_data_list = json.load(f)

        return User.from_dict(user_data_list)
