'''Library of SphericalVoronoi benchmarking functions.'''

import math
import numpy as np
import time
import scipy
from scipy.spatial import SphericalVoronoi
import cPickle as pickle
import scipy.optimize

def calculate_haversine_distance_between_spherical_points(cartesian_array_1,cartesian_array_2,sphere_radius):
    '''Calculate the haversine-based distance between two points on the surface of a sphere. Should be more accurate than the arc cosine strategy. See, for example: http://en.wikipedia.org/wiki/Haversine_formula'''
    spherical_array_1 = convert_cartesian_array_to_spherical_array(cartesian_array_1)
    spherical_array_2 = convert_cartesian_array_to_spherical_array(cartesian_array_2)
    lambda_1 = spherical_array_1[1]
    lambda_2 = spherical_array_2[1]
    phi_1 = spherical_array_1[2]
    phi_2 = spherical_array_2[2]
    #we rewrite the standard Haversine slightly as long/lat is not the same as spherical coordinates - phi differs by pi/4
    spherical_distance = 2.0 * sphere_radius * math.asin(math.sqrt( ((1 - math.cos(phi_2-phi_1))/2.) + math.sin(phi_1) * math.sin(phi_2) * ( (1 - math.cos(lambda_2-lambda_1))/2.)  ))
    return spherical_distance

def convert_cartesian_array_to_spherical_array(coord_array,angle_measure='radians'):
    '''Take shape (N,3) cartesian coord_array and return an array of the same shape in spherical polar form (r, theta, phi). Based on StackOverflow response: http://stackoverflow.com/a/4116899
    use radians for the angles by default, degrees if angle_measure == 'degrees' '''
    spherical_coord_array = np.zeros(coord_array.shape)
    xy = coord_array[...,0]**2 + coord_array[...,1]**2
    spherical_coord_array[...,0] = np.sqrt(xy + coord_array[...,2]**2)
    spherical_coord_array[...,1] = np.arctan2(coord_array[...,1], coord_array[...,0])
    spherical_coord_array[...,2] = np.arccos(coord_array[...,2] / spherical_coord_array[...,0])
    if angle_measure == 'degrees':
        spherical_coord_array[...,1] = np.degrees(spherical_coord_array[...,1])
        spherical_coord_array[...,2] = np.degrees(spherical_coord_array[...,2])
    return spherical_coord_array

def convert_spherical_array_to_cartesian_array(spherical_coord_array,angle_measure='radians'):
    '''Take shape (N,3) spherical_coord_array (r,theta,phi) and return an array of the same shape in cartesian coordinate form (x,y,z). Based on the equations provided at: http://en.wikipedia.org/wiki/List_of_common_coordinate_transformations#From_spherical_coordinates
    use radians for the angles by default, degrees if angle_measure == 'degrees' '''
    cartesian_coord_array = np.zeros(spherical_coord_array.shape)
    #convert to radians if degrees are used in input (prior to Cartesian conversion process)
    if angle_measure == 'degrees':
        spherical_coord_array[...,1] = np.deg2rad(spherical_coord_array[...,1])
        spherical_coord_array[...,2] = np.deg2rad(spherical_coord_array[...,2])
    #now the conversion to Cartesian coords
    cartesian_coord_array[...,0] = spherical_coord_array[...,0] * np.cos(spherical_coord_array[...,1]) * np.sin(spherical_coord_array[...,2])
    cartesian_coord_array[...,1] = spherical_coord_array[...,0] * np.sin(spherical_coord_array[...,1]) * np.sin(spherical_coord_array[...,2])
    cartesian_coord_array[...,2] = spherical_coord_array[...,0] * np.cos(spherical_coord_array[...,2])
    return cartesian_coord_array

def generate_spherical_points(num_points):
    # generate uniform points on sphere (see:
    # http://stackoverflow.com/a/23785326/2942522)
    np.random.seed(123)
    points = np.random.normal(size=(num_points, 3))
    points /= np.linalg.norm(points, axis=1)[:, np.newaxis]
    return points

def calculate_surface_area_of_a_spherical_Voronoi_polygon(array_ordered_Voronoi_polygon_vertices,sphere_radius):
    '''Calculate the surface area of a polygon on the surface of a sphere. Based on equation provided here: http://mathworld.wolfram.com/LHuiliersTheorem.html
    Decompose into triangles, calculate excess for each'''
    #have to convert to unit sphere before applying the formula
    spherical_coordinates = convert_cartesian_array_to_spherical_array(array_ordered_Voronoi_polygon_vertices)
    spherical_coordinates[...,0] = 1.0
    array_ordered_Voronoi_polygon_vertices = convert_spherical_array_to_cartesian_array(spherical_coordinates)
    #handle nearly-degenerate vertices on the unit sphere by returning an area close to 0 -- may be better options, but this is my current solution to prevent crashes, etc.
    #seems to be relatively rare in my own work, but sufficiently common to cause crashes when iterating over large amounts of messy data
    if scipy.spatial.distance.pdist(array_ordered_Voronoi_polygon_vertices).min() < (10 ** -7):
        print 'Problematic spherical polygon SA calculation.'
        return 10 ** -8
    else:
        n = array_ordered_Voronoi_polygon_vertices.shape[0]
        #point we start from
        root_point = array_ordered_Voronoi_polygon_vertices[0]
        totalexcess = 0
        #loop from 1 to n-2, with point 2 to n-1 as other vertex of triangle
        # this could definitely be written more nicely
        b_point = array_ordered_Voronoi_polygon_vertices[1]
        root_b_dist = calculate_haversine_distance_between_spherical_points(root_point, b_point, 1.0)
        for i in 1 + np.arange(n - 2):
            a_point = b_point
            b_point = array_ordered_Voronoi_polygon_vertices[i+1]
            root_a_dist = root_b_dist
            root_b_dist = calculate_haversine_distance_between_spherical_points(root_point, b_point, 1.0)
            a_b_dist = calculate_haversine_distance_between_spherical_points(a_point, b_point, 1.0)
            s = (root_a_dist + root_b_dist + a_b_dist) / 2.
            try:
                totalexcess += 4 * math.atan(math.sqrt( math.tan(0.5 * s) * math.tan(0.5 * (s-root_a_dist)) * math.tan(0.5 * (s-root_b_dist)) * math.tan(0.5 * (s-a_b_dist))))
            except ValueError:
                return 10 ** -8
        return totalexcess * (sphere_radius ** 2)

def percent_surface_area_analysis(max_num_generators, num_tests, outfile_name):
    generator_counts = np.logspace(1, np.log10(max_num_generators), num=num_tests)
    list_percent_reconstitutions = []
    list_generator_counts = []
    for generator_count in generator_counts:
        generator_count = int(generator_count)
        list_generator_counts.append(generator_count)
        random_generators = generate_spherical_points(generator_count)
        print 'running SA % reconstitution analysis for', generator_count, 'generators'
        sv = scipy.spatial.SphericalVoronoi(random_generators)
        sv.sort_vertices_of_regions()
        reconstituted_area = 0
        for region in sv.regions:
            polygon = sv.vertices[region]
            area = calculate_surface_area_of_a_spherical_Voronoi_polygon(polygon, 1.0)
            reconstituted_area += area
        theoretical_area = 4. * np.pi
        reconstituted_area = (float(reconstituted_area) / theoretical_area) * 100.
        list_percent_reconstitutions.append(reconstituted_area)
    percent_reconstitutions = np.array(list_percent_reconstitutions)
    generator_counts = np.array(list_generator_counts)
    pickle.dump((generator_counts, percent_reconstitutions), open(outfile_name,
        'wb'))

def benchmark_SphericalVoronoi(max_num_generators, num_tests, num_repeats,
                               outfile_name):
    generator_counts = np.logspace(1, np.log10(max_num_generators), num=num_tests)
    dict_performance_measures = {}
    for generator_count in generator_counts:
        generator_count = int(generator_count)
        random_generators = generate_spherical_points(generator_count)
        list_execution_times = [] # in seconds
        print 'running benchmarks for', generator_count, 'generators'
        for trial in range(num_repeats):
            start = time.time()
            scipy.spatial.SphericalVoronoi(random_generators)
            end = time.time()
            list_execution_times.append(end - start)
        array_execution_times = np.array(list_execution_times)
        avg_execution_time = np.average(array_execution_times)
        std_execution_time = np.std(array_execution_times)
        dict_performance_measures[generator_count] = {'avg':avg_execution_time,
                                                      'std':std_execution_time}
    pickle.dump(dict_performance_measures, open(outfile_name, 'wb'))

def fit_time_complexity(scipy_019_bench_data):

    def loglinear(n, K):
        '''Loglinear fit with K as the constant.'''
        return K * (n * np.log(n))

    def linear(n, K):
        '''Linear fit with K as the constant.'''
        return K * n

    def quadratic(n, K):
        '''Quadratic fit with K as the constant.'''
        return K * (n ** 2)

    x_data = []
    y_data = []
    for generator_count, subdict in scipy_019_bench_data.iteritems():
        x_data.append(generator_count)
        y_data.append(subdict['avg'])
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    sorter = np.argsort(x_data)
    x_data = x_data[sorter]
    y_data = y_data[sorter]

    K_loglinear, pcov_loglinear = scipy.optimize.curve_fit(loglinear,
            x_data, y_data)
    K_linear, pcov_linear = scipy.optimize.curve_fit(linear,
            x_data, y_data)
    K_quadratic, pcov_quadratic = scipy.optimize.curve_fit(quadratic,
            x_data, y_data)

    sample_x_data = np.logspace(1, np.log10(x_data.max() + 1e7), num=250)
    sample_y_data_loglinear = loglinear(sample_x_data, K_loglinear[0])
    sample_y_data_linear = linear(sample_x_data, K_linear[0])
    sample_y_data_quadratic = quadratic(sample_x_data, K_quadratic[0])

    return_dict = {'sample_x_data':sample_x_data,
                   'loglinear':sample_y_data_loglinear, 
                   'linear':sample_y_data_linear,
                   'quadratic':sample_y_data_quadratic}
    return return_dict


