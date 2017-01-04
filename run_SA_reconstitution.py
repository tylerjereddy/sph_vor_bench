'''Run the % surface area reconstitution analysis for scipy 0.19
SphericalVoronoi code.'''
import scipy
import benchlib

if '0.19' in scipy.__version__:
    benchlib.percent_surface_area_analysis(max_num_generators=1e7,
                                           num_tests=40,
                                           outfile_name='area_019.p')
else:
    print 'Invalid scipy version for %SA analysis'
