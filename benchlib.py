'''Library of SphericalVoronoi benchmarking functions.'''

import numpy as np
import time
import scipy
from scipy.spatial import SphericalVoronoi
import cPickle as pickle
import scipy.optimize

def generate_spherical_points(num_points):
    # generate uniform points on sphere (see:
    # http://stackoverflow.com/a/23785326/2942522)
    np.random.seed(123)
    points = np.random.normal(size=(num_points, 3))
    points /= np.linalg.norm(points, axis=1)[:, np.newaxis]
    return points

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

    sample_x_data = np.linspace(1, x_data.max(), num=50)
    sample_y_data_loglinear = loglinear(sample_x_data, K_loglinear[0])
    sample_y_data_linear = linear(sample_x_data, K_linear[0])
    sample_y_data_quadratic = quadratic(sample_x_data, K_quadratic[0])

    return_dict = {'sample_x_data':sample_x_data,
                   'loglinear':sample_y_data_loglinear, 
                   'linear':sample_y_data_linear,
                   'quadratic':sample_y_data_quadratic}
    return return_dict


