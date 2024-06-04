import numpy as np
import matplotlib.pyplot as plt

def flat2llh(xn, yn, mu0, l0):
    # Converts local NED (North, East, Down) coordinates to latitude and longitude using a reference point
    l0 = np.radians(l0)  # Convert longitude reference point to radians
    mu0 = np.radians(mu0)  # Convert latitude reference point to radians

    # WGS-84 parameters
    r_e = 6378137  # Semi-major axis (equatorial radius)
    e = 0.0818  # Eccentricity

    # Calculate meridian and transverse radii of curvature
    Rn = r_e / np.sqrt(1 - e ** 2 * np.sin(mu0) ** 2)
    Rm = Rn * (1 - e ** 2) / np.sqrt(1 - e ** 2 * np.sin(mu0) ** 2)

    # Convert distances to angles
    dl = yn * np.arctan2(1, Rm*np.cos(mu0))
    dmu = xn * np.arctan2(1, Rn)

    # Convert back to degrees
    l = np.rad2deg(l0 + dl)
    mu = np.rad2deg(mu0 + dmu)

    return mu, l

def euclidean_distance(point1, point2):
    # Calculate Euclidean distance between two points
    return ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5

def read_out_boundaries_from_occupancy_grid(occupancy_grid):
    # Find the boundaries of the occupancy grid
    boundaries = []
    for i in range(occupancy_grid.shape[0]-1):
        for j in range(occupancy_grid.shape[1]-1):
            # Check if the cell to the right or below is different from the current cell
            if occupancy_grid[i,j] != occupancy_grid[i,j+1] or occupancy_grid[i,j] != occupancy_grid[i+1,j]:
                # Add boundary coordinates (adjust for origin)
                boundaries.append((617-i-0.5,j+0.5))
    return boundaries

def define_land_polygons_from_boundaries(boundaries):
    # Define polygons from boundary points
    points_list_copy = boundaries.copy()
    polygons_dict = {}
    polygon_number = 0
    current_point = points_list_copy.pop(0)
    polygons_dict[polygon_number] = [current_point]

    while points_list_copy:
        smallest_distance = float('inf')
        for point in points_list_copy:
            distance_to_current_point = euclidean_distance(current_point, point)
            if distance_to_current_point < smallest_distance:
                smallest_distance = distance_to_current_point
                closest_point = point
        if smallest_distance > 20.0:
            polygon_number += 1
            current_point = points_list_copy.pop(0)
            polygons_dict[polygon_number] = [current_point]
        else:
            polygons_dict[polygon_number].append(closest_point)
            current_point = closest_point
            points_list_copy.remove(closest_point)
    
    polygons_dict[3].append((1.5,800))  # Add specific point to polygon 3
    return polygons_dict

def convert_polygon_dict_into_WGS_84(polygons_dict, ned_origin):
    # Convert polygon coordinates from local NED to WGS 84
    polygon1 = []
    polygon2 = []
    polygon3 = []
    polygon4 = []
    for i in range(4):
        for point in polygons_dict[i]:
            mu, l = flat2llh(point[0], point[1], ned_origin[0], ned_origin[1])
            if i == 0:
                polygon1.append((mu,l))
            elif i == 1:
                polygon2.append((mu,l))
            elif i == 2:
                polygon3.append((mu,l))
            elif i == 3:
                polygon4.append((mu,l))

    land_polygon = {}
    land_polygon[1] = polygon1
    land_polygon[2] = polygon2 + polygon3[::-1]  # Combine and reverse polygon3
    land_polygon[3] = polygon4
    return land_polygon

def plot_occupancy_grid(occupancy_grid, origin_x, origin_y, show=True):
    # Plot the occupancy grid with radar origin
    plt.imshow(occupancy_grid, cmap='binary', interpolation='none', origin='upper', extent=[0, occupancy_grid.shape[1], 0, occupancy_grid.shape[0]])
    plt.scatter(origin_x, origin_y, marker="x", color="red", label="Radar")
    if show:
        plt.show()