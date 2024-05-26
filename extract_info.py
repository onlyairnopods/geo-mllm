import json
import yaml
from tqdm import tqdm
import re
import ast
from abc import ABC, abstractmethod

from method import *
from utils import init_log

logger = init_log('global')

class BaseProcess(ABC):
    @abstractmethod
    def process_data(self, input_json_path, output_json_path, method, model):
        print(str(input_json_path))
        print(str(output_json_path))
        print(str(method))
        print(str(model))
    
class OriginProcess(BaseProcess):
    def process_data(self, input_json_path, output_json_path, method, model):
        with open(input_json_path, "r") as file:
            json_data = json.load(file)
        method = METHOD_DICT[method]
        extract_json = []
        cnt = 0
        for ds in tqdm(json_data):
            if ds:
                cnt += 1
                photo = ds['photo'].replace(' ', '_')
                owner = ds['owner']
                originalformat = ds['originalformat']
                if originalformat == 'null':
                    originalformat = 'jpg'
                image_file = f"{photo}_{owner}.{originalformat}"
                latitude = ds['latitude']
                longitude = ds['longitude']
            
                unit = {}
                unit['image_file'] = image_file

                unit[model] = method(latitude, longitude).to_dict()

                extract_json.append(unit)

        with open(output_json_path, 'w') as json_file:
            json.dump(extract_json, json_file, indent=4)

        logger.info(f"{len(json_data)} files totally, {cnt} files done! {len(json_data) - cnt} files are None. {len(extract_json)} files are extracted.")

class ExtractProcess(BaseProcess):
    def process_data(self, input_json_path, output_json_path, method, model):
        with open(input_json_path, "r") as file:
            json_data = json.load(file)

        cnt = 0
        for ds in tqdm(json_data):
            if ds:
                try:
                    text = ds[model][method]['output']
                    ds[model][method].update(METHOD_DICT[method](text).to_dict())
                    cnt += 1
                except:
                    continue
                
        with open(output_json_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

        logger.info(f"{len(json_data)} files totally, {cnt} files done! {len(json_data) - cnt} files left.")

class JsonProcessor:
    def __init__(self, config_path):
        with open(config_path, 'r') as cfg_file:
            cfg = yaml.safe_load(cfg_file)

        self.method = cfg['method']['name']
        self.model = cfg['model']['name']
        self.get_origin = cfg.get('get_origin', False)

        self.input_json_path = cfg['infer_json_path']
        self.output_json_path = cfg['re_json_path']

    def process_json(self):
        if self.get_origin:
            OriginProcess().process_data(self.input_json_path, self.output_json_path, method='basic', model='gt')
        else:
            ExtractProcess().process_data(self.input_json_path, self.output_json_path, method=self.method, model=self.model)




if __name__ == "__main__":
    json_process = JsonProcessor('./config.yaml').process_json()