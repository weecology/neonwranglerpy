import numpy as np
import h5py
import os
import rasterio
from rasterio.transform import Affine


def h5refl2array(refl_filename, remove_water_bands=True):
    """
    Extract metadata from h5 object and reflectance values
    returns: metadata and a numpy array
    """
    hdf5_file = h5py.File(refl_filename, 'r')
    file_attrs_string = str(list(hdf5_file.items()))
    file_attrs_string_split = file_attrs_string.split("'")
    sitename = file_attrs_string_split[1]
    solar_angles = tile_solar_angle(refl_filename)
    #Extract the reflectance & wavelength datasets
    reflArray = hdf5_file[sitename]['Reflectance']
    wavelengths = reflArray['Reflectance_Data'][:]
    # get file's EPSG
    epsg = str(reflArray['Metadata']['Coordinate_System']['EPSG Code'][()])
    #reflArray['Metadata']['Coordinate_System'].keys()
    # Create dictionary containing relevant metadata information
    metadata = {}
    metadata['mapInfo'] = reflArray['Metadata']['Coordinate_System']['Map_Info'][()]
    metadata['wavelength'] = reflArray['Metadata']['Spectral_Data']['Wavelength'][()]
    metadata['shape'] = wavelengths.shape

    #Extract no data value & scale factor
    metadata['noDataVal'] = float(
        reflArray['Reflectance_Data'].attrs['Data_Ignore_Value'])
    metadata['scaleFactor'] = float(reflArray['Reflectance_Data'].attrs['Scale_Factor'])

    #metadata['interleave'] = reflData.attrs['Interleave']
    metadata['bad_band_window1'] = np.array([1340, 1445])
    metadata['bad_band_window2'] = np.array([1790, 1955])
    metadata['epsg'] = str(epsg)

    mapInfo_string = str(metadata['mapInfo'])
    mapInfo_split = mapInfo_string.split(",")
    epsg = epsg.split("'")[1]

    #get tiles for BRDF correction
    sns_az = hdf5_file[sitename]['Reflectance/Metadata/to-sensor_azimuth_angle'][()]
    sns_zn = hdf5_file[sitename]['Reflectance/Metadata/to-sensor_zenith_angle'][()]
    #get solar angles as array to leverage flightpaths mosaic
    flightpaths = hdf5_file[sitename][
        'Reflectance/Metadata/Ancillary_Imagery/Data_Selection_Index'][()]
    sol_zn = hdf5_file[sitename][
        'Reflectance/Metadata/Ancillary_Imagery/Data_Selection_Index'][()]
    sol_az = hdf5_file[sitename][
        'Reflectance/Metadata/Ancillary_Imagery/Data_Selection_Index'][()]
    for pt in range(len(solar_angles)):
        sol_az[flightpaths == solar_angles[pt][0]] = solar_angles[pt][1]
        sol_zn[flightpaths == solar_angles[pt][0]] = solar_angles[pt][2]


#
    mapInfo_string = str(metadata['mapInfo'])
    mapInfo_split = mapInfo_string.split(",")
    mapInfo_split
    #
    # Extract the resolution & convert to floating decimal number
    metadata['res'] = {}
    metadata['res']['pixelWidth'] = float(mapInfo_split[5])
    metadata['res']['pixelHeight'] = float(mapInfo_split[6])

    # Extract the upper left-hand corner coordinates from mapInfo
    xMin = float(mapInfo_split[3])  # convert from string to floating point number
    yMax = float(mapInfo_split[4])

    # Calculate the xMax and yMin values from the dimensions
    xMax = xMin + (metadata['shape'][1] * metadata['res']['pixelWidth'])
    # xMax = left edge + (# of columns * resolution)",
    yMin = yMax - (metadata['shape'][0] * metadata['res']['pixelHeight'])
    # yMin = top edge - (# of rows * resolution)",
    metadata['extent'] = (xMin, xMax, yMin, yMax)  # useful format for plotting
    metadata['ext_dict'] = {}
    metadata['ext_dict']['xMin'] = xMin
    metadata['ext_dict']['xMax'] = xMax
    metadata['ext_dict']['yMin'] = yMin
    metadata['ext_dict']['yMax'] = yMax
    metadata['epsg'] = epsg
    reflArray = reflArray['Reflectance_Data'][()]
    hdf5_file.close()

    return (reflArray, metadata, sol_az, sol_zn, sns_az, sns_zn)


def tile_solar_angle(full_path):
    hdf5_file = h5py.File(full_path, 'r')
    file_attrs_string = str(list(hdf5_file.items()))
    file_attrs_string_split = file_attrs_string.split("'")
    sitename = file_attrs_string_split[1]
    flight_paths = hdf5_file[sitename][
        "Reflectance/Metadata/Ancillary_Imagery/Data_Selection_Index"].attrs["Data_Files"]
    flight_paths = str(flight_paths).split(",")
    which_paths = np.unique(
        hdf5_file[sitename]["Reflectance/Metadata/Ancillary_Imagery/Data_Selection_Index"]
        [()])
    solar_angle = []
    for pt in which_paths:
        #if pt is negative, get any from the available to avoid error(the pixel is blank anyway)
        if pt < 0:
            flight = (flight_paths)[which_paths[-1]].split("_")[5]
        else:
            flight = (flight_paths)[pt].split("_")[5]
        #
        sol_az = hdf5_file[sitename]["Reflectance/Metadata/Logs/"][str(
            flight)]["Solar_Azimuth_Angle"][()]
        sol_zn = hdf5_file[sitename]["Reflectance/Metadata/Logs/"][str(
            flight)]["Solar_Zenith_Angle"][()]
        solar_angle.append([pt, sol_az, sol_zn])
    return (solar_angle)


def stack_subset_bands(reflArray, reflArray_metadata, bands, clipIndex):
    subArray_rows = clipIndex['yMax'] - clipIndex['yMin']
    subArray_cols = clipIndex['xMax'] - clipIndex['xMin']

    stackedArray = np.zeros((subArray_rows, subArray_cols, len(bands)), dtype=np.int16)
    band_clean_dict = {}
    band_clean_names = []

    for i in range(len(bands)):
        band_clean_names.append("b" + str(bands[i]) + "_refl_clean")
        band_clean_dict[band_clean_names[i]] = subset_clean_band(
            reflArray, reflArray_metadata, clipIndex, bands[i])
        stackedArray[..., i] = band_clean_dict[band_clean_names[i]]

    return stackedArray


def subset_clean_band(reflArray, reflArray_metadata, clipIndex, bandIndex):
    bandCleaned = reflArray[clipIndex['yMin']:clipIndex['yMax'],
                            clipIndex['xMin']:clipIndex['xMax'],
                            bandIndex - 1].astype(np.int16)

    return bandCleaned


#    array2raster(tilename, hyperspec_raster, sub_meta, clipExtent, save_dir)


def array2raster(newRaster,
                 reflBandArray,
                 reflArray_metadata,
                 extent,
                 ras_dir,
                 invert_axes=True):
    """
    newRaster: filename of the raster object
    reflBandArray: Clipped wavelength data,
    reflArray_metadata: Clipped wavelength metadata
    extent: The UTM coordinate extent
    ras_dir: Where to save the file
    """
    print(reflBandArray.shape)
    if invert_axes is True:
        cols = reflBandArray.shape[1]
        rows = reflBandArray.shape[0]
        bands = reflBandArray.shape[2]
        reflBandArray = np.moveaxis(reflBandArray, 2, 0)
    else:
        cols = reflBandArray.shape[1]
        rows = reflBandArray.shape[2]
        bands = reflBandArray.shape[0]

    originX = extent['xMin']
    originY = extent['yMax']
    res = reflArray_metadata['res']['pixelWidth']
    transform = Affine.translation(originX, originY) * Affine.scale(res, -res)
    with rasterio.open(
            "{}/{}".format(ras_dir, newRaster),
            'w',
            driver='GTiff',
            height=rows,
            width=cols,
            count=bands,
            dtype=reflBandArray.dtype,
            crs=rasterio.crs.CRS.from_dict(init='epsg:' +
                                           str(reflArray_metadata["epsg"])),
            transform=transform,
    ) as dst:
        dst.write(reflBandArray)
    return (reflBandArray)


def calc_clip_index(clipExtent, h5Extent, xscale=1, yscale=1):
    """Extract numpy index for the utm coordinates"""
    h5rows = h5Extent['yMax'] - h5Extent['yMin']
    h5cols = h5Extent['xMax'] - h5Extent['xMin']

    ind_ext = {}
    ind_ext['xMin'] = round((clipExtent['xMin'] - h5Extent['xMin']) / xscale)
    ind_ext['xMax'] = round((clipExtent['xMax'] - h5Extent['xMin']) / xscale)
    ind_ext['yMax'] = round(h5rows - (clipExtent['yMin'] - h5Extent['yMin']) / yscale)
    ind_ext['yMin'] = round(h5rows - (clipExtent['yMax'] - h5Extent['yMin']) / yscale)

    return ind_ext


def generate_raster(h5_path,
                    save_dir,
                    rgb_filename=None,
                    bands="no_water",
                    correction="all",
                    bounds=False,
                    suffix=None):
    """
    h5_path: input path to h5 file on disk
    bands: "all" bands or "false color", "no_water" bands
    save_dir: Directory to save raster object
    rgb_filename= Path to rgb image to draw extent and crs definition
    
    returns: True if saved file exists
    """
    if suffix:
        suffix = "_{}".format(suffix)
    else:
        suffix = ""
    #Get numpy array and metadata
    refl, metadata, sol_az, sol_zn, sns_az, sns_zn = h5refl2array(h5_path)
    #Select nanometers RGB see NeonTreeEvaluation/utilities/neon_aop_bands.csv
    if bands == "no_water":
        #Delete water absorption bands
        rgb = np.r_[0:425]
        rgb = np.delete(rgb, np.r_[419:425])
        rgb = np.delete(rgb, np.r_[283:315])
        rgb = np.delete(rgb, np.r_[192:210])
    elif bands == "false_color":
        rgb = [16, 54, 112]
    elif bands == "all":
        rgb = np.r_[0:426]
    else:
        raise ValueError("no band combination specified")

    refl = refl[:, :, rgb]
    xmin, xmax, ymin, ymax = metadata['extent']

    #Optional clip
    if bounds:
        #Set extent in utm
        clipExtent = {}
        clipExtent['xMin'] = bounds.left
        clipExtent['xMax'] = bounds.right
        clipExtent['yMin'] = bounds.bottom
        clipExtent['yMax'] = bounds.top
    else:
        clipExtent = {}
        clipExtent['xMin'] = xmin
        clipExtent['xMax'] = xmax
        clipExtent['yMin'] = ymin
        clipExtent['yMax'] = ymax
    #Get hyperspectral array extent with respect to the pixel index
    subInd = calc_clip_index(clipExtent, metadata['ext_dict'])
    #Turn to integer
    for x in subInd:
        subInd[x] = int(subInd[x])

    #Index numpy array of hyperspec reflectance and the solar/sensor angle rasters
    refl = refl[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax'], :]
    sol_az = sol_az[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax']]
    sol_zn = sol_zn[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax']]
    sns_az = sns_az[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax']]
    sns_zn = sns_zn[(subInd['yMin']):subInd['yMax'], (subInd['xMin']):subInd['xMax']]

    #Create new filepath
    if bands == "false_color":
        tilename = os.path.splitext(
            os.path.basename(rgb_filename))[0] + "_false_color{}.tif".format(suffix)
    else:
        tilename = os.path.splitext(
            os.path.basename(rgb_filename))[0] + "_hyperspectral{}.tif".format(suffix)

    #stach solar and sensor data to be used for corrections
    sol_sens_angle = np.array([sol_az, sol_zn, sns_az, sns_zn])
    solar_tilename = os.path.splitext(
        os.path.basename(rgb_filename))[0] + "_solar_sensor_angle{}.tif".format(suffix)
    #Save georeference crop to file
    array2raster(solar_tilename,
                 sol_sens_angle,
                 metadata,
                 clipExtent,
                 save_dir,
                 invert_axes=False)
    array2raster(tilename, refl, metadata, clipExtent, save_dir, invert_axes=True)
