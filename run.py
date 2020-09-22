import pandas as pd
from rasterio import MemoryFile
import geopandas as gpd
import numpy as np
from rasterio.transform import Affine
from rasterstats import zonal_stats as zs
import rasterio as rio
import os

# Define paths
data_path = '/data'
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')

# Read CityCAT results
data = pd.read_csv(os.path.join(inputs_path, 'run/R1C1_SurfaceMaps/R1_C1_max_depth.csv'))

# Convert CityCAT results to GeoTIFF
# GDAL XYZ driver does not represent missing data properly so converting manually
unique_x, x_inverse = np.unique(data.XCen.values, return_inverse=True)
unique_y, y_inverse = np.unique(data.YCen.values, return_inverse=True)
x_size, y_size = len(unique_x), len(unique_y)
y_inverse = y_size - y_inverse - 1
nodata = -9999
depth = np.full((y_size, x_size), nodata, dtype=float)
depth[y_inverse, x_inverse] = data.Depth.values
res = unique_x[1] - unique_x[0]

with MemoryFile() as f:
    with rio.open(
        f,
        'w',
        driver='GTiff',
        height=y_size,
        width=x_size,
        count=1,
        dtype=depth.dtype,
        transform=Affine.translation(data.XCen.min(), data.YCen.max()) * Affine.scale(res, -res),
        nodata=nodata
    ) as dst:
        dst.write(depth, 1)

    with f.open() as src:
        # Read buildings data
        buildings = gpd.read_file(os.path.join(inputs_path, 'mastermap/mastermap-topo_3629050_0.gpkg'), bbox=src.bounds,
                                  layer='TopographicArea')

        # Extract maximum depths for each building from CityCAT results
        buildings['depth'] = [row['max'] for row in zs(buildings, src.read(1), affine=src.transform, stats=['max'],
                                                       all_touched=True, nodata=nodata)]

        # Save a copy of buildings data with a new depth field
        buildings.to_file(os.path.join(outputs_path, 'building-depths.gpkg'), driver='GPKG')
