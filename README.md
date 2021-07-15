# Flood Impacts DAFNI Model

[![build](https://github.com/OpenCLIM/flood-impacts-dafni/workflows/build/badge.svg)](https://github.com/OpenCLIM/flood-impacts-dafni/actions)

## Features
- [Read buildings from OS MasterMap](#mastermap)
- [Read buildings from UDM urban fabric](#udm)
- [Select buildings intersecting flood extent](#filter)
- [Calculate maximum depth and depth-velocity product](#depth)
- [Calculate length of flooded perimeter](#perimeter)
- [Lookup UPRNs for each TOID](#uprn)

## Parameters
The following parameters must be provided as environment variables (in uppercase and with spaces replaced by underscores). 
See [model-definition.yml](https://github.com/OpenCLIM/flood-impacts-dafni/blob/master/model-definition.yml) for further details.
- Threshold

## Dataslots
Data is made available to the model at the following paths. The spatial projection of all datasets is assumed to be the same. 
- inputs/MasterMap
- inputs/buildings/urban_fabric.gpkg
- inputs/run/max_depth.tif
- inputs/uprn
- inputs/dd-curves

## Usage 
`docker build -t flood-impacts-dafni . && docker run -v "data:/data" --env PYTHONUNBUFFERED=1 --env THRESHOLD=0.1 --name flood-impacts-dafni flood-impacts-dafni `

## <a name="mastermap">Read buildings from OS MasterMap</a>
The data contained in a single GPKG file in the `MasterMap` dataslot is read using GeoPandas.
If more than one file is provided then only the first file alphabetically will be used.

## <a name="udm">Read buildings from UDM urban fabric</a>
If the file `inputs/buildings/urban_fabric.gpkg` exists, its features are appended to those in the MasterMap layer. 
The urban fabric features are assumed to be polygons and are assigned OIDs of `udm` followed by their index position in 
the dataset.

## <a name="filter">Select buildings intersecting flood extent</a>
Each building is buffered by 5m.
Flooded areas are created as polygons where depths exceed the `THRESHOLD` using `rasterio.features.shapes`. These 
flooded areas are then intersected with the buildings to identify buildings which are inundated over the `THRESHOLD`.

## <a name="depth">Calculate maximum depth and depth-velocity product</a>
The `zonal_stats` function from the `rasterstats` package is used to find the maximum intersecting flood depth and
depth velocity product from the rasters at `inputs/run/max_depth.tif` and `inputs/run/max_vd_product.tif` within 5m of 
each polygon in the `MasterMap` layer (optionally combined with the urban fabric).

## <a name="perimeter">Calculate damages</a>
Depths at each building are converted into a damage (£) using the CSV files in the `dd-curves` dataslot. Buildings with
a MISTRAL `building_use` of residential are assigned damage values based on the `residential.csv` curve. All other buildings
are assigned damaged values based on the `nonresidential.csv` file. Both CSV files are assumed to contain columns names
`depth` and `damage`, with depths in metres and damages in £/m<sup>2</sup>.

## <a name="perimeter">Calculate length of flooded perimeter</a>
The intersection of the buffered building polygon boundaries and the flooded areas is calculated using 
`geopandas.overlay`. The length of these lines is the flooded perimeter.

## <a name="uprn">Lookup UPRNs for each TOID</a>
If a file is provided in the `UPRN` dataslot, this is used to lookup the Unique Property Reference Numbers (UPRNs) for
each building. Each building may have more than one UPRN and therefore more than one row in the output CSV.

The maximum depth, maximum depth velocity product and flooded perimeter values are stored in the `buildings.csv` output 
file by building oid and uprn (if provided).
