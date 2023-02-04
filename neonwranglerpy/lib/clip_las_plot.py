"""Tools for reading and clipping NEON LiDAR data."""
import laspy
import numpy as np

def clip_raster(plt, data_path, buffer, savepath):
    """Given a Laz file, clip it by the size of the input plot.
    
    Parameters:
    plt = string with at least easting and northing of the center of the target plot
    data_path =  path in which the laz/las file is stored
    buffer = the buffer around the center of the plot (plot size divided by 2)
    savepath =  full path where to store the clipped laz file.
    
    """
    # open the NEON las tile
    las = laspy.read(data_path)
    # builds the bounding box with center (easting, northing)
    center_x, center_y = plt['easting'], plt['northing']
    minx, miny = center_x - buffer, center_y - buffer
    maxx, maxy = center_x + buffer, center_y + buffer

    # make sure the max and min are not outside the boudaries of the tile
    minx, miny = max(minx, las.header.mins[0]), max(miny, las.header.mins[1])
    maxx, maxy = min(maxx, las.header.maxs[0]), min(maxy, las.header.maxs[1])

    clip_x = (minx < las.x) & (maxx > las.x)
    clip_y = (miny < las.y) & (maxy > las.y)
    clip_z = (las.header.max[2] > las.z) & (las.header.min[2] < las.z)

    good_indices = np.where(clip_x & clip_y &clip_z)

    # clip las around the coordinates
    clip = las.points[good_indices[0]].copy()

    # save file
    output_file = laspy.LasData(las.header)
    output_file.points = clip
    output_file.write(savepath)
    return(output_file)




