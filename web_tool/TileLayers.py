import os

import fiona
import shapely.geometry
from enum import Enum

from web_tool.frontend_server import ROOT_DIR

def load_geojson_as_list(fn):
    shapes = []
    crs = None
    with fiona.open(fn) as f:
        crs = f.crs
        for row in f:
            shape = shapely.geometry.shape(row["geometry"])
            shapes.append(shape)
    return shapes, crs

class DataLayerTypes(Enum):
    ESRI_WORLD_IMAGERY = 1
    USA_NAIP_LIST = 2
    CUSTOM = 3

'''
This dictionary defines how the backend tool will return data to the frontend.

An entry is formated like below:

"LAYER NAME": {
    "data_layer_type": DataLayerTypes.ESRI_WORLD_IMAGERY,
    "shapes_fn": None,
    "data_fn": None,
    "shapes": None,  # NOTE: this is always `None` and populated automatically when this file loads (see code at bottom of file)
    "shapes_crs": None  # NOTE: this is always `None` and populated automatically when this file loads (see code at bottom of file)
    "padding": None # NOTE: this is optional and only used in DataLayerTypes.CUSTOM
}

LAYER_NAME - should correspond to an entry in js/tile_layers.js
data_layer_type -  should be an item from the DataLayerTypes enum and describes where the data comes from.
  - If ESRI_WORLD_IMAGERY then the backend will lookup imagery from the ESRI World Imagery basemap and not respond to requests for downloading
  - If USA_NAIP_LIST then the backend will lookup imagery from the full USA tile_index (i.e. how we usually do it) and requests for downloading will be executed on the same tiles
  - If CUSTOM then the backend will query the "shapes_fn" and "data_fn" files for how/what to download, downloading will happen similarlly
shapes_fn - should be a path, relative to `frontend_server.ROOT_DIR`, of a geojson defining shapes over which the data_fn file is valid. When a "download" happens the raster specified by "data_fn" will be masked with one of these shapes.
data_fn - should be a path, relative to `frontend_server.ROOT_DIR`, of a raster file defining the imagery to use
shapes - list of `shapely.geometry.shape` objects created from the shapes in "shapes_fn".
shapes_crs - the CRS of the shapes_fn
padding - NOTE: Optional, only used in DataLayerTypes.CUSTOM - defines the padding used in raster extraction, used to get the required 240x240 input
'''
DATA_LAYERS = {
    "esri_world_imagery": { 
        "data_layer_type": DataLayerTypes.ESRI_WORLD_IMAGERY,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "esri_world_imagery_naip": { 
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "osm": {
        "data_layer_type": DataLayerTypes.ESRI_WORLD_IMAGERY,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "chesapeake": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "demo_set_1": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "user_study_1": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "user_study_2": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "user_study_3": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "user_study_4": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "user_study_5": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": "shapes/user_study_5_outline.geojson",
        "data_fn": "tiles/user_study_5.tif",
        "shapes": None,
        "shapes_crs": None,
        "padding": 20
    },
    "philipsburg_mt": {
        "data_layer_type": DataLayerTypes.USA_NAIP_LIST,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "yangon": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": "shapes/yangon_grid_shapes.geojson",
        "data_fn": "tiles/yangon.tif",
        "shapes": None,
        "shapes_crs": None,
        "padding": 1100
    },
    "aceh": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": None,
        "data_fn": None,
        "shapes": None,
        "shapes_crs": None
    },
    "hcmc": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": "shapes/hcmc_wards.geojson",
        "data_fn": "tiles/HCMC.tif",
        "shapes": None,
        "shapes_crs": None
    },
    "hcmc_sentinel": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": "shapes/hcmc_sentinel_districts.geojson",
        "data_fn": "tiles/hcmc_sentinel.tif",
        "shapes": None,
        "shapes_crs": None,
        "padding": 1100
    },
    "yangon_lidar": {
        "data_layer_type": DataLayerTypes.CUSTOM,
        "shapes_fn": "shapes/yangon_wards.geojson",
        "data_fn": "tiles/yangon_lidar.tif",
        "shapes": None,
        "shapes_crs": None
    }
}

for k in DATA_LAYERS.keys():
    if DATA_LAYERS[k]["shapes_fn"] is not None:
        fn = os.path.join(ROOT_DIR, DATA_LAYERS[k]["shapes_fn"])
        if os.path.exists(fn):
            shapes, crs = load_geojson_as_list(fn)
            DATA_LAYERS[k]["shapes"] = shapes
            DATA_LAYERS[k]["shapes_crs"] = crs["init"]
        else:
            print("WARNING: %s doesn't exist, this server will not be able to serve the '%s' dataset" % (fn, k))        