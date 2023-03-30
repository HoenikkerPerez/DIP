"""
Windows: 
    & 'C:\Program Files\Blender Foundation\Blender 3.3\blender.exe' -b -P recon_all_clean.py -- True
"""
import bpy
import math
import os
import numpy as np
import itertools
import random
import sys

from resources.Config import Config
from renderer.Render import Render
from loader.Loader import Loader

def get_random_rgb_colors(n_total, seed=42):
    random.seed(seed)
    return [(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1) for _ in range(n_total)]


def run_all():
    config = Config("config.json")
    print(config)
    renderer = Render(config.get("render_engine"))
    meshes = Loader.get_meshes(config.get("datasets"))
    colors = get_random_rgb_colors(len(meshes), seed=42)
    for i, (path, filename) in enumerate(meshes):
        color = colors[i]
        for material in config.get("materials"):
            renderer.render_multiview_single_scene(path, 
                                                    filename, 
                                                    material, 
                                                    color,
                                                    debug=config.get("DEBUG"), 
                                                    light_disposition=config.get("light_disposition"), 
                                                    materials_path=config.get("materials_path"),
                                                    background_type=config.get("environment_type"),
                                                    background_image_path=config.get("background_image"),
                                                    output_render_dir=config.get("render_dir"),
                                                    camera_model=config.get("camera_model"),
                                                    exiftool_filepath=config.get("exiftool_path"),
                                                    default_materials=config.get("materials"))
            if config.get("DEBUG"):
                return


if __name__ == "__main__":
    run_all()