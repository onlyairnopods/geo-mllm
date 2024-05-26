import re
import ast

from utils import trans_float

class Basic:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude
        }
    
class Direct(Basic):
    def __init__(self, text):
        # 正则表达式匹配
        reasoning_process_match = re.search(r'Reasoning process = (\[.*?\])', text)
        result_match = re.search(r'The most likely locations = (\[.*?\])', text)
        if result_match == None:
            result_match = re.search(r'The most likely location: (\[.*?\])', text)
            if result_match == None:
                result_match = re.search(r'### The most likely location:\s*\n\n(.+?), ([\d\.]+)° N, ([\d\.]+)° E', text)
        
        # 将字符串表示的列表转换为Python列表对象
        # reasoning_process = ast.literal_eval(reasoning_process_match.group(1))
        # print(result_match)
        # result = ast.literal_eval(result_match.group(1))

        location, latitude, longitude = result_match.group(1), result_match.group(2), result_match.group(3)
        
        latitude = trans_float(latitude)
        longitude = trans_float(longitude)
        if (latitude == None) | (longitude == None):
            raise ValueError
        
        super().__init__(latitude, longitude)
        self.location = location

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                'location': self.location
            }
        )
        return base_dict

class Top5(Basic):
    def __init__(self, text):
        reasoning_process_match = re.search(r'Reasoning process = (\[.*?\])', text)
        top_cities_match = re.search(r'Top 5 most likely cities = (\[.*?\])', text)

        if top_cities_match == None:
            top_cities_match = re.search(r'Top 5 most likely locations = (\[.*?\])', text)

        # 将字符串表示的列表转换为Python列表对象
        # reasoning_process = ast.literal_eval(reasoning_process_match.group(1))
        top_cities = ast.literal_eval(top_cities_match.group(1))

        location = [city[0] for city in top_cities]
        latitudes = [city[1] for city in top_cities]
        longitudes = [city[2] for city in top_cities]

        latitudes = trans_float(latitudes)
        longitudes = trans_float(longitudes)
        if (latitudes == None) | (longitudes == None):
            raise ValueError

        super().__init__(latitudes, longitudes)
        self.location = location

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                'location': self.location
            }
        )
        return base_dict

    def get_prompt(ds, n):
        prompt_1 = "Question: Where was this image taken?\n"
        lens = min(len(ds["location"]), len(ds["latitude"]), len(ds["longitude"]))
        for num in range(lens):
            city = ds['location'][num]
            latitude = ds['latitude'][num]
            longitude = ds['longitude'][num]
            prompt_1 += f"({num + 1}) {city}, {latitude}, {longitude} "
        prompt_1s = prompt_1 + "\n"

        prompt_2 = '\nUse the image as context and answer the following question:\n'
        prompt_2 = prompt_2 + prompt_1s + "\nAnswer with the option's number from the given choices directly.\n"
        return prompt_2

METHOD_DICT = {
    'basic': Basic,
    'direct': Direct,
    'top5': Top5,
}