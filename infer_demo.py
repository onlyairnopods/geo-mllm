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

# Heatmap
import folium
from folium.plugins import HeatMap

from model import get_model
from utils import init_log
from method import *

logger = init_log('global')

parser = argparse.ArgumentParser()
parser.add_argument("--image-path", type=str, help='path to test image')
args = parser.parse_args()

def main(args, config_path):
    with open(config_path, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    api_key = cfg['model'].get('api_key', None)
    model_name = cfg['model']['name']
    method = cfg['method']['name']
    round = cfg['method'].get('round', 1)
    model = get_model(model_name)

    with open(cfg['prompt'], 'r') as prompt_file:
        prompt = prompt_file.read()

    # if round > 1:
    #     prompt = Top5.get_prompt(ds[model_name][method], round)

    img = PIL.Image.open(args.image_path)

    try:
        res = model(prompts=[img, prompt], api_key=api_key)
    except:
        logger.info(f'Model inference error')
        return
    
    field = 'output' if round == 1 else 'street_num'
    ds = {model_name: {method: {field: res}}}

    text = ds[model_name][method]['output']

    ds[model_name][method].update(METHOD_DICT[method](text).to_dict())

    latitude = ds[model_name][method]['latitude']
    longitude = ds[model_name][method]['longitude']
    location = ds[model_name][method]['location']

    logger.info(f'This image was taken at {location}, {latitude}°, {longitude}° ')

    return(latitude, longitude)

# borrowed from: https://colab.research.google.com/drive/1p3f5F3fIw9CD7H4RvfnHO9g-J45qUPHp?usp=sharing
def visualize(latitude, longitude):
    # Set top coordinates to plot the heatmap (<= top_k)
    # top_n_coordinates = 10

    # gps_coordinates = top_pred_gps.tolist()[:top_n_coordinates]
    # probabilities = top_pred_prob.tolist()[:top_n_coordinates]

    # total_prob = sum(probabilities)
    # normalized_probs = [prob / total_prob for prob in probabilities]

    # # Combine coordinates with normalized probabilities
    # weighted_coordinates = [(lat, lon, weight) for (lat, lon), weight in zip(gps_coordinates, normalized_probs)]

    # # Calculate the average location to center the map
    # avg_lat = sum(lat for lat, lon, weight in weighted_coordinates) / len(weighted_coordinates)
    # avg_lon = sum(lon for lat, lon, weight in weighted_coordinates) / len(weighted_coordinates)

    # Create a map centered around the average coordinates
    m = folium.Map(location=[latitude, longitude], zoom_start=2.2)

    weighted_coordinates = [(latitude, longitude, 1.)]

    # Define the color gradient
    magma = {
        0.0: '#932667',
        0.2: '#b5367a',
        0.4: '#d3466b',
        0.6: '#f1605d',
        0.8: '#fd9668',
        1.0: '#fcfdbf'
    }

    HeatMap(weighted_coordinates, gradient=magma).add_to(m)

    # Mark top coordinate
    top_coordinate = [latitude, longitude]

    folium.Marker(
        location=top_coordinate,
        popup=f"Top Prediction: {top_coordinate}",
        icon=folium.Icon(color='orange', icon='star')
    ).add_to(m)

    # # Display the map
    # m

    # Save the map to an HTML file
    m.save('map.html')

    # Optionally, automatically open the file in the default web browser
    import webbrowser
    webbrowser.open(f'map.html', new=2)


if __name__ == "__main__":
    config_path = "./config.yaml"
    coordinates = main(args, config_path)
    visualize(*coordinates)