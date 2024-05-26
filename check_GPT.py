from pprint import pprint
from openai import OpenAI
import json
import time
from tqdm import tqdm
import yaml

from utils import init_log

logger = init_log('global')

def convert_keys_to_lower(d):
    if isinstance(d, dict):
        return {k.lower(): convert_keys_to_lower(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_lower(i) for i in d]
    else:
        return d

def ask_GPT(ask_text, prompt_path, model, api_key):
    # print(ask_text)

    client = OpenAI(
    api_key=api_key,
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": open(f"{prompt_path}/system_prompt.txt").read()},

            {"role": "user", "name":"example_user", "content": open(f"{prompt_path}/user1.txt").read()},
            {"role": "assistant", "name": "example_assistant", "content": open(f"{prompt_path}/assistant1.txt").read()},

            {"role": "user", "name":"example_user", "content": open(f"{prompt_path}/user2.txt").read()},
            {"role": "assistant", "name": "example_assistant", "content": open(f"{prompt_path}/assistant2.txt").read()},

            {"role": "user", "name":"example_user", "content": open(f"{prompt_path}/user3.txt").read()},
            {"role": "assistant", "name": "example_assistant", "content": open(f"{prompt_path}/assistant3.txt").read()},

            {"role": "user", "name":"example_user", "content": open(f"{prompt_path}/user4.txt").read()},
            {"role": "assistant", "name": "example_assistant", "content": open(f"{prompt_path}/assistant4.txt").read()},

            # {"role": "user", "content": open("./prompt_TOP5_new/user5.txt").read()},
            # {"role": "assistant", "content": open("./prompt_TOP5_new/assistant5.txt").read()},
            
            {"role": "user", "content": ask_text}
        ],
        # seed=114514,
    )
    try:
        json_content = json.loads(completion.choices[0].message.content)
    except ValueError:
        return completion.choices[0].message.content, "None"
    
    json_content = convert_keys_to_lower(json_content)
    return completion.choices[0].message.content, json_content


def main(config_path):
    with open(config_path, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    method = cfg['method']['name']
    model = cfg['model']['name']

    check_model = cfg['check_model']['name']
    api_key = cfg['check_model']['api_key']

    input_json_path = cfg['re_json_path']
    output_json_path = cfg['check_json_path']

    prompt_path = cfg['check_prompt_path']

    # debug
    debug = cfg['debug']['mode']
    debug_idx = cfg['debug'].get('test_instances', 0)

    with open(input_json_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    cnt = 0
    for idx, ds in enumerate(tqdm(json_data)):
        if idx < 0:
            continue

        if debug and idx > debug_idx:
            break

        if not ('latitude' in ds[model][method]):
            cnt += 1
            try:
                answer, json_answer = ask_GPT(ds[model][method]['output'], prompt_path, check_model, api_key)
            except:
                continue
            if json_answer == "None" or answer == "0.0":
                continue

            ds[model][method].update(json_answer)
        
            with open(output_json_path, 'w', encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4)

    logger.info(cnt)

if __name__ == "__main__":
    main('./config.yaml')