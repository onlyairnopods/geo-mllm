import pathlib
import textwrap
import json
import os
import google.generativeai as genai
import time
import argparse

from IPython.display import display
from IPython.display import Markdown
import PIL.Image
from tqdm import tqdm


def gemini(prompts, api_key, idx=None, txt_path=None):
    genai.configure(api_key=api_key) # 这里是api-key
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(
        prompts,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            top_p=0.7
        ),
        safety_settings={
            'HARASSMENT':'block_none',
        }
    )

    try:
        # print(response.text)
        return response.text
    except ValueError:
        if idx and txt_path:
            # print(response.prompt_feedback)
            with open(txt_path, 'a') as wfile:
                wfile.write(str(idx) + ": "  + str(response.prompt_feedback) + '\n')
        return "None"


def get_model(model_name):
    if model_name == 'gemini':
        model = gemini
    else:
        raise NotImplementedError(f"model {model_name} is not supported.")

    return model