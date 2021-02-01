import geopandas as gpd
from rasterstats import zonal_stats as zs
import rasterio as rio
import os
from rasterio import features
import numpy as np
from shapely.geometry import shape
import glob

# Define paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)
mastermap = glob.glob(os.path.join(inputs_path, 'mastermap', '*.gpkg'))[0]
area_layer = 'Topographicarea'
line_layer = 'Topographicline'
output_file = os.path.join(outputs_path, 'features.gpkg')

threshold = float(os.getenv('THRESHOLD'))

buffer = 5

with rio.open(os.path.join(inputs_path, 'run/max_depth.tif')) as src:
    # Read MasterMap data
    areas = gpd.read_file(mastermap, bbox=src.bounds, layer=area_layer).rename(columns={'fid': 'toid'})
    lines = gpd.read_file(mastermap, bbox=src.bounds, layer=line_layer).rename(columns={'fid': 'toid'})

    # Read flood depths
    depth = src.read(1)

    # Extract maximum depths for each building
    areas['depth'] = [row['max'] for row in zs(areas.buffer(buffer), depth, affine=src.transform, stats=['max'],
                                               all_touched=True, nodata=src.nodata)]

    # Find areas flooded above threshold
    flooded_areas = gpd.GeoDataFrame(
        geometry=[shape(s[0]) for s in features.shapes(
            np.ones(depth.shape, dtype=rio.uint8), mask=depth >= threshold, transform=src.transform)], crs=src.crs)

    # Filter areas and intersect lines
    areas = areas[areas.depth >= threshold]
    lines = gpd.overlay(lines, flooded_areas)

    # Save a copy of lines and areas to the GeoPackage
    if len(areas) > 0:
        areas.to_file(output_file, layer=area_layer, driver='GPKG')
    if len(lines) > 0:
        lines.to_file(output_file, layer=line_layer, driver='GPKG')

    # Count the number of areas by featurecode and save to CSV
    areas.featurecode.value_counts().rename_axis('featurecode').rename('count').to_csv(
        os.path.join(outputs_path, 'counts.csv'))

    # Count the total inundated distances by featurecode and save to CSV
    lines.geometry.length.groupby(lines.featurecode).sum().round(2).rename('distance (m)').to_csv(
        os.path.join(outputs_path, 'distance.csv'))
