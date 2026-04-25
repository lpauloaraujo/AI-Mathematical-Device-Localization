import sys
import os
import csv
import json
import random
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from domain.base_station import BaseStation
from domain.user import User

def generate_bs(csv_path):
    bs_list = []
    id_bs = 1
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bs = BaseStation(
                identifier=str(id_bs),
                x=float(row['Longitude']),
                y=float(row['Latitude']),
                height=float(row['AlturaAntena']),
                gain=float(row['GanhoAntena']),
                frequency=900,
                power=40
            )
            bs_list.append(bs)
            id_bs += 1
    return bs_list

def generate_user_point(lat, lon, max_distance=300):

    distance = random.uniform(0, max_distance)
    angle = random.uniform(0, 2 * math.pi)

    dx = distance * math.cos(angle)
    dy = distance * math.sin(angle)

    delta_lat = dy / 111320
    delta_lon = dx / (111320 * math.cos(math.radians(lat)))

    return lon + delta_lon, lat + delta_lat

def generate_points_from_json(json_path, points_per_bs=100):
    with open(json_path, "r") as f:
        stations = json.load(f)

    users = []

    for bs in stations:
        lat = bs["y"]
        lon = bs["x"]

        for _ in range(points_per_bs):
            user_lon, user_lat = generate_user_point(lat, lon)

            users.append(User(
                x=user_lon,
                y=user_lat,
                height=1.5,
                gain=0,
            ))

    return users

def generate_users_json(csv_path, output_path="data/users_generation_result.json",
                        height=1.5, gain=0):
    users = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                lat = float(row["lat real"])
                lon = float(row["long real"])
            except (ValueError, KeyError):
                continue 

            user = {
                "x": lat,
                "y": lon,
                "height": height,
                "gain": gain
            }

            users.append(user)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(users, f, indent=4)

    print(f"{len(users)} usuários gerados em {output_path}")

def save_json(obj_list, file_path):
    data = [obj.to_dict() for obj in obj_list]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

estacoes = generate_bs('data/estacoes_trilateracao.csv')
users = generate_points_from_json('data/generated_bs.json', points_per_bs=100)
print(len(users))
#generate_users_json('data/trilateration_table.csv', output_path='data/generated_users.json')

save_json(estacoes, 'data/generated_bs.json')
save_json(users, 'data/generated_users.json')

table = "data/trilateration_table.csv"

linha1 = [
    "lat real", "long real", "server", "rssi", 
    "Neighbor 1", "rssi", 
    "Neighbor 2", "rssi", 
    "lat calc", "long calc", "Erro (%)", "fallback"
]

with open(table, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)  
    
    writer.writerow(linha1)

    for user in users:
        linha = [
            user.y,     
            user.x,       
            "", "",       
            "", "",       
            "", "",       
            "", "",        
            "", ""       
        ]

        writer.writerow(linha)

print("CSV criado com sucesso!")