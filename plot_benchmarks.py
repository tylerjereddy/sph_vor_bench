import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np

scipy_0181_bench_data = pickle.load(open('bench_018.p', 'rb'))
scipy_019_bench_data = pickle.load(open('bench_019.p', 'rb'))

fig = plt.figure()
ax1 = fig.add_subplot('111')
for condition, bench_dict in zip(['scipy 0.18.1', 'scipy 0.19'], [scipy_0181_bench_data,
                                 scipy_019_bench_data]):
    x_values = []
    y_values = []
    y_err_values = []
    for generator_count, subdict in bench_dict.iteritems():
        x_values.append(generator_count)
        y_values.append(subdict['avg'])
        y_err_values.append(subdict['std'])
    x_values = np.array(x_values)
    y_values = np.array(y_values)
    y_err_values = np.array(y_err_values)
    sorter = np.argsort(x_values)
    x_values = x_values[sorter]
    y_values = y_values[sorter]
    y_err_values = y_err_values[sorter]
    ax1.errorbar(x_values, y_values, yerr=y_err_values, marker='o',
            label=condition, markeredgecolor='None')
ax1.legend(loc=2)
ax1.set_xlabel('log(generators)')
ax1.set_ylabel('Time to Produce Voronoi Regions (s)')
ax1.set_xscale('log')
ax1.set_xlim(1,10**8)
ax1.annotate('dengue', (4000, 5), (400, 50), arrowprops =dict(arrowstyle="->"),fontsize = 10) #approx. dengue leaflet size
ax1.annotate('influenza A', (20000, 12), (1000, 70), arrowprops = dict(arrowstyle="->"),fontsize = 10) #approx. flu leaflet size indicator
# add vertical line at scipy 0.18.1 physical memory consumption limit
# on rMBP 
ax1.axvline(x=9e4, lw=4, color='grey', ls='--')
fig.savefig('fig_benchmarks.png', dpi=300)
