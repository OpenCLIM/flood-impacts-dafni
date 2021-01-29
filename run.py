import pandas as pd
import geopandas as gpd
from rasterstats import zonal_stats as zs
import rasterio as rio
import os

# Define paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')
mastermap = os.path.join(inputs_path, 'mastermap/mastermap-topo_3889921.gpkg')
area_layer = 'Topographicarea'
line_layer = 'Topographicline'
output_file = os.path.join(outputs_path, 'depths.gpkg')

threshold = os.getenv('THRESHOLD', 0.01)

buffer = 5

with rio.open(os.path.join(inputs_path, 'run/max_depth.tif')) as src:
    # Read buildings data

    areas = gpd.read_file(mastermap, bbox=src.bounds, layer=area_layer).rename(columns={'fid': 'toid'})
    lines = gpd.read_file(mastermap, bbox=src.bounds, layer=line_layer).rename(columns={'fid': 'toid'})
    depth = src.read(1)

    # Extract maximum depths for each building from CityCAT results
    areas['depth'] = [row['max'] for row in zs(areas.buffer(buffer), depth, affine=src.transform, stats=['max'],
                                               all_touched=True, nodata=src.nodata)]

    lines['depth'] = [row['max'] for row in zs(lines.buffer(buffer), depth, affine=src.transform, stats=['max'],
                                               all_touched=True, nodata=src.nodata)]

    areas = areas[areas.depth >= threshold]
    lines = lines[lines.depth >= threshold]

    # Save a copy of buildings data with a new depth field
    if len(areas) > 0:
        areas.to_file(output_file, layer=area_layer, driver='GPKG')
    if len(lines) > 0:
        lines.to_file(output_file, layer=line_layer, driver='GPKG')

    df = pd.concat([areas, lines])
    df.to_csv(os.path.join(outputs_path, 'depths.csv'), index=False)
    df.featurecode.value_counts().to_csv(os.path.join(outputs_path, 'counts.csv'))
