import json
import operator
from pprint import pprint
from tqdm import tqdm
import yaml
from geopy.distance import geodesic

def update_res(result, distance):
    # 注意: 一个距离可能会被统计多次
    if distance.km <= 1.0:
        result["1km"] += 1
    if distance.km <= 25.0:
        result["25km"] += 1
    if distance.km <= 200.0:
        result["200km"] += 1
    if distance.km <= 750.0:
        result["750km"] += 1
    if distance.km <= 2500.0:
        result["2500km"] += 1

    return distance.km, result

def calc_min_dis(ds, model_name, method, location_true, latitudes, longitudes):
    if not (type(latitudes) is list):
        latitudes = [latitudes]
    if not (type(longitudes) is list):
        longitudes = [longitudes]

    if len(latitudes) == 0:
        latitudes.append(0.0)
    if len(longitudes) == 0:
        longitudes.append(0.0)

    # try:
    #     latitudes = [latitudes[ds["street_img_num"] - 1]]
    #     longitudes = [longitudes[ds["street_img_num"] - 1]]
    #     City = ds["city.1"][ds["street_img_num"] - 1]
    # except:
    #     try:
    #         latitudes = [latitudes[ds["img_num"] - 1]]
    #         longitudes = [longitudes[ds["img_num"] - 1]]
    #         City = ds["city.2"][ds["img_num"] - 1]
    #     except:
    #         latitudes = [latitudes[0]]
    #         longitudes = [longitudes[0]]
    #         City = "unknown"

    try:
        location = ds[model_name][method]['location']
    except:
            latitudes = [latitudes[0]]
            longitudes = [longitudes[0]]
            location = "unknown"

    number_of_locations = min(len(latitudes), len(longitudes), 1)
    assert(number_of_locations == 1), f"number_of_locations: {number_of_locations}"

    distances = []

    for idx in range(number_of_locations):
        location = (latitudes[idx], longitudes[idx])
        try:
            distances.append(geodesic(location_true, location))
        except:
            distances.append(geodesic(location_true, (0.0, 0.0)))

    return min(distances)

def main(config_path):
    with open(config_path, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    model_name = cfg['model']['name']
    method = cfg['method']['name']

    with open(cfg['check_json_path'], "r", encoding="utf-8") as file:
        json_data = json.load(file)

    dist_result = dict()
    dist_result["1km"] = 0
    dist_result["25km"] = 0
    dist_result["200km"] = 0
    dist_result["750km"] = 0
    dist_result["2500km"] = 0

    num = len(json_data)

    for idx, ds in enumerate(tqdm(json_data)):
        try:
            location_true = (float(ds['gt']["latitude"]), float(ds['gt']["longitude"]))
        except:
            num -= 1
            continue

        # latitudes_2 = [0.0 for i in range(5)]
        # if "latitudes.1" in ds:
        #     latitudes_2 = ds["latitudes.1"]
        # elif "latitudes.2" in ds:
        #     latitudes_2 = ds["latitudes.2"]

        # longitudes_2 = [0.0 for i in range(5)]
        # if "longitudes.1" in ds:
        #     longitudes_2 = ds["longitudes.1"]
        # elif "longitudes.2" in ds:
        #     longitudes_2 = ds["longitudes.2"]
        
        # distance_gemini = calc_min_dis(ds, location_true, latitudes_2, longitudes_2)

        try:
            latitude = ds[model_name][method]['latitude']
            longitude = ds[model_name][method]['longitude']
        except KeyError:
            break

        distance_gemini = calc_min_dis(ds, model_name, method, location_true, latitude, longitude)

        dis_gemini, dist_result = update_res(dist_result, distance_gemini)

        # print(dis_gemini)

    # 转换成百分比
    for k in dist_result:
        dist_result[k] = float(dist_result[k]) / float(num) * 100.0
        dist_result[k] = round(dist_result[k], 2)

    print(dist_result)

if __name__ == "__main__":
    main('./config.yaml')