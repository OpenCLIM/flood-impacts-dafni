import pandas as pd
from rasterio import MemoryFile
import geopandas as gpd
import numpy as np
from rasterio.transform import Affine
from rasterstats import zonal_stats as zs
import rasterio as rio

data = pd.read_csv('/data/inputs/citycat/R1C1_SurfaceMaps/R1_C1_max_depth.csv')

# GDAL XYZ driver not working so creating raster manually
unique_x, x_inverse = np.unique(data['XCen'].values, return_inverse=True)
unique_y, y_inverse = np.unique(data['YCen'].values, return_inverse=True)
x_size, y_size = len(unique_x), len(unique_y)
y_inverse = y_size - y_inverse - 1
missing_data = -9999
depth = np.full((y_size, x_size), missing_data, dtype=float)
depth[y_inverse, x_inverse] = data.Depth.values
res = unique_x[1] - unique_x[0]
f = MemoryFile()
with rio.open(
    f,
    'w',
    driver='GTiff',
    height=y_size,
    width=x_size,
    count=1,
    dtype=depth.dtype,
    transform=Affine.translation(data.XCen.min(), data.YCen.max()) * Affine.scale(res, -res),
    nodata=missing_data
) as dst:
    dst.write(depth, 1)

with f.open() as src:
    buildings = gpd.read_file('/data/inputs/mastermap/mastermap-topo_3629050_0.gpkg', bbox=src.bounds,
                              layer='TopographicArea')

    buildings['depth'] = [row['max'] for row in zs(buildings, src.read(1), affine=src.transform, stats=['max'],
                                                   all_touched=True, nodata=missing_data)]

    buildings.to_file('/data/outputs/building-depths.gpkg', driver='GPKG')
