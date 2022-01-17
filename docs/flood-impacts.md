## Flood Impacts DAFNI Model

Calculates maximum depths, velocity depth products (VD) and flooded perimeters of flooded buildings. Each building is buffered by 5m to extract surrounding depths and VDs. Flooded areas are created as polygons where flood depths exceed the provided `THRESHOLD`. The intersection of the buffered building polygon boundaries and the flooded areas is then calculated. The length of these lines is the flooded perimeter. This length is converted to a percentage of the total perimeter of each building.

## Parameters

| name      | title               | description                                              |
|:----------|:--------------------|:---------------------------------------------------------|
| THRESHOLD | Threshold depth (m) | Minimum water depth used to assign buildings as flooded. |

## Dataslots

| path             | name                         | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|:-----------------|:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| inputs/mastermap | MasterMap                    | OS MasterMap buildings geopackage. Must contain a 'toid' attribute. The data must be contained in a single GPKG file. If more than one file is provided then only the first file alphabetically will be used.                                                                                                                                                                                                                                                                                                             |
| inputs/buildings | UDM Buildings                | If the file "urban_fabric.gpkg" exists, its features are appended to those in the MasterMap layer. The urban fabric features are assumed to be polygons and are assigned OIDs of `udm` followed by their index position in the dataset.                                                                                                                                                                                                                                                                                   |
| inputs/uprn      | UPRN                         | Lookup between TOID and UPRN identifiers (CSV). If provided, this is used to lookup the Unique Property Reference Numbers (UPRNs) for each building. Each building may have more than one UPRN and therefore more than one row in the output CSV.                                                                                                                                                                                                                                                                         |
| inputs/dd-curves | Depth/damage curves          | CSV files named residential.csv and nonresidential.csv relating depth (m) to damage (£/m2) Depths at each building are converted into a damage (£) using these curves. Buildings with a MISTRAL `building_use` of residential are assigned damage values based on the `residential.csv` curve. All other buildings are assigned damaged values based on the `nonresidential.csv` file. Both CSV files are assumed to contain columns names `depth` and `damage`, with depths in metres and damages in £/m<sup>2</sup>. |
| inputs/run       | Maximum depth and VD rasters | Maximum depth and maximum depth velocity product rasters in GeoTIFF format. The files must be named "max_depth.tif" and "max_vd_product.tif".                                                                                                                                                                                                                                                                                                                                                                             |

## Outputs

| name                  | description                                                                                                                                                                                                    |
|:----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| outputs/buildings.csv | Maximum depths & velocity depth products and flooded perimeters of flooded buildings The maximum depth, maximum VD, flooded perimeter and damage values are stored in `buildings.csv` by building oid or uprn. |