'''Run the SphericalVoronoi benchmarks.'''

import benchlib
import scipy

version = scipy.__version__

if '0.18.1' in version:
    benchlib.benchmark_SphericalVoronoi(max_num_generators=90000,
                                        num_tests=5,
                                        num_repeats=5,
                                        outfile_name='bench_018.p')
elif '0.19' in version:
    benchlib.benchmark_SphericalVoronoi(max_num_generators=1e6,
                                        num_tests=5,
                                        num_repeats=5,
                                        outfile_name='bench_019.p')
else:
    print 'Invalid scipy version for benchmarks:', version
