# Flood Impacts DAFNI Model

[![build](https://github.com/OpenCLIM/flood-impacts-dafni/workflows/build/badge.svg)](https://github.com/OpenCLIM/flood-impacts-dafni/actions)

## Features
- [Read polygons and lines from OS MasterMap](#mastermap)
- [Read polygons from UDM urban fabric](#udm)
- [Calculate depths at polygons](#depth)
- [Find distances of lines above threshold depth](#distance)
- [Create GPKG of inundated features](#gpkg)
- [Create CSVs of building counts and road distances by feature code](#csv)

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

## <a name="mastermap">Read polygons and lines from OS MasterMap</a>
The data contained in a single GPKG file in the `MasterMap` dataslot is read using GeoPandas.
If more than one file is provided then only the first file alphabetically will be used.
Only features in the `Topographicarea` and `Topographicline` layers are included, all other features are ignored.

## <a name="udm">Read polygons from UDM urban fabric</a>
If the file `inputs/buildings/urban_fabric.gpkg` exists, its features are appended to those in the `Topographicarea` 
MasterMap layer. The urban fabric features are assumed to be polygons and are assigned a feature code of 20000.

## <a name="depth">Calculate depths at polygons</a>
The `zonal_stats` function from the `rasterstats` package is used to find the maximum intersecting flood depth from the 
raster at `inputs/run/max_depth.tif` for each polygon in the `Topographicarea` layer (optionally combined with the urban 
fabric).

## <a name="distance">Find distances of lines above threshold depth</a>
`Topographicline` features are intersected with a vectorised version of `inputs/run/max_depth.tif` and the distances of 
line segments within polygons above the `THRESHOLD` depth are calculated.

## <a name="gpkg">Create GPKG of inundated features</a>
The polygons and segments of lines above the `THRESHOLD` are exported to a new GPKG file called `features.gpkg` with 
layer names matching the original MasterMap data. The polygon features also include the maximum flood depths.

## <a name="csv">Create CSVs of building counts and road distances by feature code</a>
Two CSV files are created. `counts.csv` includes the number of polygons and `distance.csv` the length of line segments 
which have a maximum depth above the `THRESHOLD`. Both counts and distances are stratified by feature code.
