# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 15:39:09 2026

@author: ameli
"""


import geopandas as gpd
import pandas as pd
from folium.plugins import HeatMap
import folium
import webbrowser
import requests

# load in data

data_file = r"C:\Users\ameli\Downloads\maps for lfl\260727 Tenant Data.csv"
letsforlife_raw = r"C:\Users\ameli\Downloads\maps for lfl\lets4life.csv"
lingtrust_raw = r"C:\Users\ameli\Downloads\maps for lfl\lingtrust.csv"
superior_raw = r"C:\Users\ameli\Downloads\maps for lfl\superior.csv"
tc_raw = r"C:\Users\ameli\Downloads\maps for lfl\transforming.csv"

pins = pd.read_csv(data_file)
letsforlife = pd.read_csv(letsforlife_raw)
lingtrust = pd.read_csv(lingtrust_raw)
superior = pd.read_csv(superior_raw)
tc = pd.read_csv(tc_raw)

# extract the uk postcodes as lat and long coords

uk_postcode_regex = r'([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})'

# function to convert postcodes to lat and long


def geocode_postcodes_bulk(postcodes):
    url = "https://api.postcodes.io/postcodes"
    results = {}
    clean_pcs = list(set(postcodes))

    for i in range(0, len(clean_pcs), 100):
        batch = clean_pcs[i:i + 100]
        response = requests.post(url, json={"postcodes": batch})
        if response.status_code == 200:
            data = response.json().get('result', [])
            for item in data:
                pc = item['query']
                res = item['result']
                if res:
                    results[pc] = (res['latitude'], res['longitude'])
                else:
                    results[pc] = (None, None)
    return results


postcode_map_upc = geocode_postcodes_bulk(
    pins['Postcode'])
postcode_map_lfl = geocode_postcodes_bulk(
    letsforlife['Post Codes'])
postcode_map_lt = geocode_postcodes_bulk(
    lingtrust['Post Codes'])
postcode_map_sup = geocode_postcodes_bulk(
    superior['Post Codes'])
postcode_map_tc = geocode_postcodes_bulk(
    tc['Post Codes'])


pins['LAT'] = pins['Postcode'].map(
    lambda x: postcode_map_upc.get(x, (None, None))[0])
pins['LONG'] = pins['Postcode'].map(
    lambda x: postcode_map_upc.get(x, (None, None))[1])

letsforlife['LAT'] = letsforlife['Post Codes'].map(
    lambda x: postcode_map_lfl.get(x, (None, None))[0])
letsforlife['LONG'] = letsforlife['Post Codes'].map(
    lambda x: postcode_map_lfl.get(x, (None, None))[1])

lingtrust['LAT'] = lingtrust['Post Codes'].map(
    lambda x: postcode_map_lt.get(x, (None, None))[0])
lingtrust['LONG'] = lingtrust['Post Codes'].map(
    lambda x: postcode_map_lt.get(x, (None, None))[1])

superior['LAT'] = superior['Post Codes'].map(
    lambda x: postcode_map_sup.get(x, (None, None))[0])
superior['LONG'] = superior['Post Codes'].map(
    lambda x: postcode_map_sup.get(x, (None, None))[1])

tc['LAT'] = tc['Post Codes'].map(
    lambda x: postcode_map_tc.get(x, (None, None))[0])
tc['LONG'] = tc['Post Codes'].map(
    lambda x: postcode_map_tc.get(x, (None, None))[1])

# convert to geodataframe
pins = gpd.GeoDataFrame(pins, geometry=gpd.points_from_xy(
    pins['LONG'], pins['LAT']), crs="EPSG:4326")
letsforlife = gpd.GeoDataFrame(letsforlife, geometry=gpd.points_from_xy(
    letsforlife['LONG'], letsforlife['LAT']), crs="EPSG:4326")
lingtrust = gpd.GeoDataFrame(lingtrust, geometry=gpd.points_from_xy(
    lingtrust['LONG'], lingtrust['LAT']), crs="EPSG:4326")
superior = gpd.GeoDataFrame(superior, geometry=gpd.points_from_xy(
    superior['LONG'], superior['LAT']), crs="EPSG:4326")
tc = gpd.GeoDataFrame(tc, geometry=gpd.points_from_xy(
    tc['LONG'], tc['LAT']), crs="EPSG:4326")

# make interactive map of UK with folium
marker_layer = folium.FeatureGroup(name="Pin Markers")
heatmap_layer = folium.FeatureGroup(name="Density HeatMap")
lfl_layer = folium.FeatureGroup(name="Lets For Life")
lt_layer = folium.FeatureGroup(name="Ling Trust")
sup_layer = folium.FeatureGroup(name="Superior Landlord")
tc_layer = folium.FeatureGroup(name="Transforming Care")

uk_map = folium.Map(location=[54.5, -3.5], zoom_start=6, tiles="OpenStreetMap")

for idx, row in pins.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['Address'],
        # 0.0 (hidden) to 1.0 (opaque)
        icon=folium.Icon(color="red", icon="info-sign", opacity=0.5)
    ).add_to(marker_layer)

for idx, row in letsforlife.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['Address'],
        # 0.0 (hidden) to 1.0 (opaque)
        icon=folium.Icon(color="orange", icon="info-sign")
    ).add_to(lfl_layer)

for idx, row in lingtrust.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['Address'],
        # 0.0 (hidden) to 1.0 (opaque)
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(lt_layer)

for idx, row in superior.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['Address'],
        # 0.0 (hidden) to 1.0 (opaque)
        icon=folium.Icon(color="pink", icon="info-sign")
    ).add_to(sup_layer)

for idx, row in tc.iterrows():
    folium.Marker(
        location=[row['LAT'], row['LONG']],
        popup=row['Address'],
        # 0.0 (hidden) to 1.0 (opaque)
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(tc_layer)

# Add a Layer Control panel in the top-right corner to toggle layers on/off

marker_layer.add_to(uk_map)
heatmap_layer.add_to(uk_map)
lfl_layer.add_to(uk_map)
lt_layer.add_to(uk_map)
sup_layer.add_to(uk_map)
tc_layer.add_to(uk_map)

folium.LayerControl().add_to(uk_map)

# Save as an HTML file and open it in browser
heat_data = pins[['LAT', 'LONG']].dropna().values.tolist()

HeatMap(heat_data, radius=25, blur=10, min_opacity=0.4).add_to(heatmap_layer)


uk_map.save("index.html")

webbrowser.open("index.html")
