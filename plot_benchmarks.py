import matplotlib.pyplot as plt
import cPickle as pickle
import numpy as np

scipy_0181_bench_data = pickle.load(open('bench_018.p', 'rb'))
scipy_019_bench_data = pickle.load(open('bench_019.p', 'rb'))
scipy_019_time_complexity_data = pickle.load(open('time_complexity.p', 'rb'))
scipy_019_area_data = pickle.load(open('area_019.p', 'rb'))

fig = plt.figure()
ax1 = fig.add_subplot('131')
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
ax1.set_ylim(-10,350)

# plot scipy 0.19 empirical time complexity fitting data
ax2 = fig.add_subplot('132')
sample_x_data = scipy_019_time_complexity_data['sample_x_data']
sample_y_data_loglinear = scipy_019_time_complexity_data['loglinear']
sample_y_data_linear = scipy_019_time_complexity_data['linear']
sample_y_data_quadratic = scipy_019_time_complexity_data['quadratic']

ax2.plot(sample_x_data, sample_y_data_linear, c = 'red', label = 'linear', alpha= 0.5, lw = 2)
ax2.plot(sample_x_data, sample_y_data_loglinear, c = 'green', label ='loglinear', alpha = 0.5, lw = 2)
ax2.plot(sample_x_data, sample_y_data_quadratic, c = 'purple', label ='quadratic', alpha = 0.5, lw = 2)
ax2.scatter(x_values, y_values, color='black')
ax2.legend(loc = 2)
ax2.set_xscale('log')
ax2.set_ylim(-10,500)
ax2.set_xlim(1,10**8)
ax2.set_xlabel('log(generators)')

ax3 = fig.add_subplot('133')
ax3.scatter(scipy_019_area_data[0], scipy_019_area_data[1])
ax3.set_ylabel('% reconstitution of surface area')
ax3.set_xlabel('log(generators)')
ax3.set_xscale('log')
ax3.set_ylim(99,100.1)
ax3.set_xlim(1,10**8)

fig.set_size_inches(18,6)
fig.savefig('fig_benchmarks.png', dpi=300)
