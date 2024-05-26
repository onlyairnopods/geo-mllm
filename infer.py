import pathlib
import textwrap
import json
import os
import google.generativeai as genai
import time
import yaml
import argparse

from IPython.display import display
from IPython.display import Markdown
import PIL.Image
from tqdm import tqdm

from model import get_model
from utils import init_log
from method import *

logger = init_log('global')

parser = argparse.ArgumentParser()
parser.add_argument("--ptr-number", "-n", type=int, default=0, help='Continue from the broken index')
args = parser.parse_args()


def main(args, config_path):
    with open(config_path, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    api_key = cfg['model'].get('api_key', None)

    json_path = cfg['json_path']
    infer_json_path = cfg['infer_json_path']
    images_path = cfg['images_path']
    count_txt_path = cfg['count_txt_path']
    ptr_txt_path = cfg['ptr_txt_path']

    model_name = cfg['model']['name']
    method = cfg['method']['name']
    round = cfg['method'].get('round', 1)
    model = get_model(model_name)

    # debug
    debug = cfg['debug']['mode']
    debug_idx = cfg['debug'].get('test_instances', 0)

    with open(json_path, "r") as file:
        json_data = json.load(file)

    with open(cfg['prompt'], 'r') as prompt_file:
        prompt = prompt_file.read()

    idx = 0 # 记录当前处理的图像在JSON数据中的索引，用于在中断后恢复处理
    cnt = 0 # 记录因数据缺失或错误而未处理成功的图像数量
    for ds in tqdm(json_data):
        if idx < args.ptr_number:
            idx += 1
            continue

        image_path = os.path.join(
            images_path, ds["image_file"]
        )
        img = PIL.Image.open(image_path)
        
        try:
            if round > 1:
                prompt = Top5.get_prompt(ds[model_name][method], round)
            
            res = model(prompts=[img, prompt], api_key=api_key, idx=idx, txt_path=ptr_txt_path)
            
            if idx % 1000 == 0:
                logger.info(res)

            field = 'output' if round == 1 else 'street_num'
            new_field = {model_name: {method: {field: res}}}

            if model_name not in ds:
                ds.update(new_field)
            else:
                if method not in ds[model_name]:
                    ds[model_name].update(new_field[model_name])
                else:
                    ds[model_name][method].update({field: res})

            with open(infer_json_path, "w") as json_file:
                json.dump(json_data, json_file, indent=4)

        except:
            cnt += 1

        img.close()

        idx += 1

        if debug and idx > debug_idx:
            break

        with open(count_txt_path, 'w') as file:
            file.write(str(idx))

    logger.info(f"{len(json_data)} files totally, {idx} files done! {cnt} files failed. {len(json_data) - idx} files left.")


if __name__ == "__main__":
    config_path = "./config.yaml"
    main(args, config_path)