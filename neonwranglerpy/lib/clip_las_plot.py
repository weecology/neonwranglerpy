import pylas
import laspy
import numpy as np
# data_path = "/home/smarconi/Downloads/NEON_D03_OSBS_DP1_400000_3280000_classified_point_cloud_colorized.laz"
def clip_raster(plt, data_path, buffer, savepath):
    #open the NEON las tile
    las = laspy.read(data_path)
    # builds the bounding box with center (easting, northing)
    center_x, center_y = plt['easting'], plt['northing']
    minx, miny = center_x - buffer, center_y - buffer
    maxx, maxy = center_x + buffer, center_y + buffer

    #make sure the max and min are not outside the boudaries of the tile
    minx, miny = max(minx, las.header.mins[0]), max(miny, las.header.mins[1])
    maxx, maxy  = min(maxx, las.header.maxs[0]), min(maxy, las.header.maxs[1])

    clip_x = (minx < las.x) & (maxx > las.x)
    clip_y = (miny < las.y) & (maxy > las.y)
    clip_z = (las.header.max[2] > las.z) & (las.header.min[2] < las.z)

    good_indices = np.where(clip_x & clip_y &clip_z)

    #clip las around the coordinates
    clip = las.points[good_indices[0]].copy()



    #save file
    output_file = laspy.LasData(las.header)
    output_file.points = clip
    output_file.write(savepath)
    return(output_file)




