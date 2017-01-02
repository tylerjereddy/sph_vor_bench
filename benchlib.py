'''Library of SphericalVoronoi benchmarking functions.'''

import numpy as np
import time
import scipy
from scipy.spatial import SphericalVoronoi
import cPickle as pickle

def generate_spherical_points(num_points):
    # generate uniform points on sphere (see:
    # http://stackoverflow.com/a/23785326/2942522)
    np.random.seed(123)
    points = np.random.normal(size=(num_points, 3))
    points /= np.linalg.norm(points, axis=1)[:, np.newaxis]
    return points

def benchmark_SphericalVoronoi(max_num_generators, num_tests, num_repeats,
                               outfile_name):
    generator_counts = np.linspace(10, max_num_generators, num=num_tests)
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
