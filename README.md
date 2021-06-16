# Flood Impacts DAFNI Model

[![build](https://github.com/OpenCLIM/flood-impacts-dafni/workflows/build/badge.svg)](https://github.com/OpenCLIM/flood-impacts-dafni/actions)

## Features
- [Read polygons and lines from OS MasterMap](#mastermap)
- [Read polygons from UDM urban fabric](#udm)
- [Calculate depths at polygons](#depth)
- [Create a CSVs of maximum building depth and depth velocity product](#csv)

## Parameters
The following parameters must be provided as environment variables (in uppercase and with spaces replaced by underscores). 
See [model-definition.yml](https://github.com/OpenCLIM/flood-impacts-dafni/blob/master/model-definition.yml) for further details.
- Threshold

## Dataslots
Data is made available to the model at the following paths. The spatial projection of all datasets is assumed to be the same. 
- inputs/MasterMap
- inputs/buildings/urban_fabric.gpkg
- inputs/run/max_depth.tif

## Usage 
`docker build -t flood-impacts-dafni . && docker run -v "data:/data" --env PYTHONUNBUFFERED=1 --env THRESHOLD=0.1 --name flood-impacts-dafni flood-impacts-dafni `

## <a name="mastermap">Read polygons OS MasterMap</a>
The data contained in a single GPKG file in the `MasterMap` dataslot is read using GeoPandas.
If more than one file is provided then only the first file alphabetically will be used.

## <a name="udm">Read polygons from UDM urban fabric</a>
If the file `inputs/buildings/urban_fabric.gpkg` exists, its features are appended to those in the `Topographicarea` 
MasterMap layer. The urban fabric features are assumed to be polygons and are assigned OIDs of `udm` followed by their
index position in the dataset.

## <a name="depth">Calculate depths at polygons</a>
The `zonal_stats` function from the `rasterstats` package is used to find the maximum intersecting flood depth and
depth velocity product from the rasters at `inputs/run/max_depth.tif` and `inputs/run/max_cs_product.tif` within 5m of 
each polygon in the `MasterMap` layer (optionally combined with the urban fabric)

## <a name="csv">Create a CSVs of maximum building depth and depth velocity product</a>
Buildings with a maximum depth below the `THRESHOLD` are removed.
The values are then stored in the `buildings.csv` output file by building oid.
