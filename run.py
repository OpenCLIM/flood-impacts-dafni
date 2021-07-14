import geopandas as gpd
from rasterstats import zonal_stats as zs
import rasterio as rio
import os
from rasterio import features
import numpy as np
from shapely.geometry import shape
import glob
import pandas as pd

# Define paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)
mastermap = glob.glob(os.path.join(inputs_path, 'mastermap', '*.gpkg'))[0]
udm_buildings = os.path.join(inputs_path, 'buildings', 'urban_fabric.gpkg')
output_file = os.path.join(outputs_path, 'features.gpkg')
uprn_lookup = glob.glob(os.path.join(inputs_path, 'uprn', '*.csv'))

threshold = float(os.getenv('THRESHOLD'))

# Set buffer around buildings
buffer = 5

with rio.open(os.path.join(inputs_path, 'run/max_depth.tif')) as max_depth,\
        rio.open(os.path.join(inputs_path, 'run/max_vd_product.tif')) as max_vd_product:
    # Read MasterMap data
    buildings = gpd.read_file(mastermap, bbox=max_depth.bounds)
    if os.path.exists(udm_buildings):
        udm_buildings = gpd.read_file(udm_buildings, bbox=max_depth.bounds)
        udm_buildings['toid'] = 'udm' + udm_buildings.index.astype(str)
        buildings = buildings.append(udm_buildings)

    # Read flood depths and vd_product
    depth = max_depth.read(1)
    vd_product = max_vd_product.read(1)

    # Find flooded areas
    flooded_areas = gpd.GeoDataFrame(
        geometry=[shape(s[0]) for s in features.shapes(
            np.ones(depth.shape, dtype=rio.uint8), mask=np.logical_and(depth >= threshold, max_depth.read_masks(1)),
            transform=max_depth.transform)], crs=max_depth.crs)

    # Buffer buildings
    buildings['geometry'] = buildings.buffer(buffer)

    # Extract maximum depth and vd_product for each building
    buildings['depth'] = [row['max'] for row in
                          zs(buildings, depth, affine=max_depth.transform, stats=['max'],
                             all_touched=True, nodata=max_depth.nodata)]

    # Filter buildings
    buildings = buildings[buildings['depth'] > 0]

    if len(buildings) == 0:
        with open(os.path.join(outputs_path, 'buildings.csv'), 'w') as f:
            f.write('')
        exit(0)

    buildings['vd_product'] = [row['max'] for row in
                               zs(buildings, vd_product, affine=max_vd_product.transform, stats=['max'],
                                  all_touched=True, nodata=max_vd_product.nodata)]

    # Get the flooded perimeter length for each building
    flooded_perimeter = gpd.overlay(gpd.GeoDataFrame({'toid': buildings.toid}, geometry=buildings.geometry.boundary,
                                                     crs=buildings.crs), flooded_areas)
    flooded_perimeter['flooded_perimeter'] = flooded_perimeter.geometry.length.round(2)

    buildings = buildings.merge(flooded_perimeter, on='toid')

    # Lookup UPRN if available
    if len(uprn_lookup) > 0:
        uprn = pd.read_csv(uprn_lookup[0], usecols=['IDENTIFIER_1', 'IDENTIFIER_2']).rename(
            columns={'IDENTIFIER_1': 'uprn', 'IDENTIFIER_2': 'toid'})

        buildings = buildings.merge(uprn)

    # Save to CSV
    buildings[['toid', *['uprn' for _ in uprn_lookup[:1]], 'depth',  'vd_product', 'flooded_perimeter']].to_csv(
        os.path.join(outputs_path, 'buildings.csv'), index=False)
