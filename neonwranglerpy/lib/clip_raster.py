"""Tools for clipping the Data."""
import json
import rasterio as rio
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg


def clip_raster(plt, data_path, buffer, savepath):
    """Clips the Raster Data for given plot."""
    # builds the bounding box with center (easting, northing)
    center_x, center_y = plt['easting'], plt['northing']
    bbox = make_bbox(center_x, center_y, buffer)
    # read raster data
    dat = rio.open(data_path)
    # creates mask and clips raster
    out_img, out_meta = mask_raster(dat, bbox)

    # saves the raster
    with rio.open(savepath, "w", **out_meta) as dest:
        dest.write(out_img)


def make_bbox(center_x, center_y, buffer):
    """Create bounding box around (easting,northing)."""
    minx, miny = center_x - buffer, center_y - buffer
    maxx, maxy = center_x + buffer, center_y + buffer

    bbox = box(minx, miny, maxx, maxy)
    return bbox


def mask_raster(raster_data, bbox):
    """Crops plots from Raster.

    Parameters
    -----------
    raster_data :raster dataset object
    bbox : shapely.geometry.polygon.Polygon

    """
    epsg = int(raster_data.crs.data['init'][5:])
    crs = raster_data.crs
    geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(epsg)['init'])
    geo = geo.to_crs(crs=crs.data['init'])

    coords = [json.loads(geo.to_json())['features'][0]['geometry']]
    out_img, out_transform = mask(dataset=raster_data, shapes=coords, crop=True)
    out_meta = raster_data.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_img.shape[1],
        "width": out_img.shape[2],
        "transform": out_transform,
        "crs": crs
    })
    return out_img, out_meta
