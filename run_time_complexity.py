'''Execute time complexity fitting code for scipy 0.19 SphericalVoronoi'''
import benchlib
import cPickle as pickle
import scipy

if '0.19' in scipy.__version__:
    scipy_019_bench_data = pickle.load(open('bench_019.p', 'rb'))
    return_dict = benchlib.fit_time_complexity(scipy_019_bench_data)
    pickle.dump(return_dict, open('time_complexity.p', 'wb'))
else:
    print 'Invalid version of scipy used for O(n) fitting.'

