"""
Script Title: web_map.py
Author: Petter Hangerhagen
Email: petthang@stud.ntnu.no
Date: July 4th, 2024
Description: This script is used to create a satellite map of the radar area. Support functions are defined in utilities.py.
"""

import folium
from folium.vector_layers import Circle
from selenium import webdriver
import time
import matplotlib.pyplot as plt
import numpy as np
import os
import utilities as util

def create_web_map(land_polygon):
    # Create an interactive web map using Folium and Selenium
    llh_fosenkaia = (63.435167, 10.393028, 39.923)

    my_map = folium.Map(location=[llh_fosenkaia[0], llh_fosenkaia[1]], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr="Google")

    folium.Marker([llh_fosenkaia[0], llh_fosenkaia[1]], popup='Radar Position').add_to(my_map)

    # Uncomment the following lines to add the polygons to the map
    folium.Polygon(locations=land_polygon[1], color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(my_map)
    folium.Polygon(locations=land_polygon[2], color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(my_map)
    folium.Polygon(locations=land_polygon[3], color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(my_map)
    save_name = "radar_map.html"
    my_map.save(save_name)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=options)  # You may need to specify the path to your Chrome driver
    current_dir = os.getcwd()
    html_path = os.path.join(current_dir, save_name)

    # driver.get("file://" + "/home/aflaptop/Desktop/google_plots/radar_map.html")
    driver.get("file://" + html_path)

    time.sleep(2)  # Wait for the map to load

    driver.save_screenshot("radar_map.png")
    driver.quit()

if __name__ == "__main__":
    current_dir = os.getcwd()
    npy_file = "occupancy_grid.npy"
    # npy_file = "occupancy_grid_without_dilating.npy"
    file = os.path.join(current_dir, npy_file)
    data = np.load(file, allow_pickle='TRUE').item()
    occupancy_grid = data["occupancy_grid"]
    origin_x = data["origin_x"]
    origin_y = data["origin_y"]

    util.plot_occupancy_grid(occupancy_grid, origin_x, origin_y, show=False)
    boundaries = util.read_out_boundaries_from_occupancy_grid(occupancy_grid)
    polygons_dict = util.define_land_polygons_from_boundaries(boundaries)
   
    llh_fosenkaia = (63.435167, 10.393028, 39.923)
    llh_map_corner = (63.43180075539984, 10.383238792419432, 39.923)

    land_polygon = util.convert_polygon_dict_into_WGS_84(polygons_dict, llh_map_corner)
    
    create_web_map(land_polygon)
