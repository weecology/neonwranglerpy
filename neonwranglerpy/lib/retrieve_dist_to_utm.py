"""Get Precise location of Trees."""
from math import pi, cos, sin


def retrieve_dist_to_utm(individualID, dista, angle, xcord, ycord):
    """Calculate the coordinates of the point ids and trigonometry."""
    # calculate coordinates from quadrant coordinates using trigonometry
    if angle <= 90:
        adj_ang = (angle * pi) / 180
        y_shift = dista * cos(adj_ang)
        x_shift = dista * sin(adj_ang)
        point_coords = [individualID, xcord + x_shift, ycord + y_shift]

    else:
        if angle > 90 and angle <= 180:
            adj_ang = ((angle - 90) * pi) / 180
            x_shift = dista * cos(adj_ang)
            y_shift = dista * sin(adj_ang)
            point_coords = [individualID, xcord + x_shift, ycord - y_shift]
        else:
            if angle > 180 and angle <= 270:
                adj_ang = ((angle - 180) * pi) / 180
                x_shift = dista * sin(adj_ang)
                y_shift = dista * cos(adj_ang)
                point_coords = [individualID, xcord - x_shift, ycord - y_shift]
            else:
                adj_ang = ((angle - 270) * pi) / 180
                x_shift = dista * cos(adj_ang)
                y_shift = dista * sin(adj_ang)
                point_coords = [individualID, xcord - x_shift, ycord + y_shift]

    return point_coords
