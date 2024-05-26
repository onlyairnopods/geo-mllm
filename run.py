import os
import time
import subprocess
import yaml

def run_script(script_name):
    try:
        result = subprocess.run(['python', script_name], check=True)
        print(f"Successfully ran {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False
    return True

while True:
    with open('./config.yaml', 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    idx = int(open(cfg['count_txt_path'], 'r').read())
    if idx >= 3000:
        break
    
    command = "python infer.py"
    command = command + " -n " + str(idx)
    os.system(command)
    time.sleep(2)

if run_script('extract_info.py'):
    run_script('check_GPT.py')
