import bokeh
from bokeh.plotting import curdoc, figure
import utils

obs = dict()
obs['label'] = 'GPM_Imerge'
obs['source'] = '/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/NRTearly/1hr-accum'
obs['data_prefix'] = 'gpm_imerg_NRTearly_'
obs['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/gpm'
obs['process_region'] = 'SEAsia'
obs['region_lat_range'] = (-10, 20)
obs['region_lon_range'] = (90, 140)

menu_data = utils.get_menu_data(data_info=obs)
layout = utils.selection_histogram()
print(menu_data)
curdoc().add_root(layout)
curdoc().title = "Selection Histogram"
