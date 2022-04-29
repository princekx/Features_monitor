import bokeh
import pandas as pd
from pandas.plotting import scatter_matrix
import datetime
import os, sys
import glob
import iris
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, CustomJS, DataRange1d, Select, HoverTool
from bokeh.models import BoxSelectTool, LassoSelectTool, Text
from bokeh.models import GeoJSONDataSource, Range1d, ColorBar, LinearColorMapper
from bokeh.palettes import Blues4, Viridis6
from bokeh.plotting import figure, show
from bokeh.models.widgets import Panel, Tabs
import numpy as np
from data_config import model_info_dicts


def flatten_list(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten_list(list_of_lists[0]) + flatten_list(list_of_lists[1:])
    return list_of_lists[:1] + flatten_list(list_of_lists[1:])


def get_menu_data(data_info=None):
    data_dir = os.path.join(data_info['data_proc_dir'], data_info['process_region'])
    pkl_files = glob.glob(os.path.join(data_dir, 'features_' + data_info['data_prefix'] + '*.pkl'))
    menu_data = {}
    menu_data['hours'] = list(set([pkl.split('_')[-1].split('.')[0] for pkl in pkl_files]))
    menu_dates = list(set([pkl.split('_')[-2] for pkl in pkl_files]))
    menu_dates.sort(reverse=True)
    menu_data['dates'] = menu_dates
    menu_data['label'] = data_info['label']
    menu_data['region_lat_range'] = data_info['region_lat_range']
    menu_data['region_lon_range'] = data_info['region_lon_range']
    return menu_data


def get_pkl_data(date_label, hour, data_info=None):
    data_folder = os.path.join(data_info['data_proc_dir'], data_info['process_region'])
    pickle_file = os.path.join(data_folder, 'features_' + data_info['data_prefix']
                               + '%s_%s.pkl' % (date_label, hour))
    if os.path.exists(pickle_file):
        df = pd.read_pickle(pickle_file)
        df['DateLabel'] = [d.strftime("%Y/%m/%d") for d in df.Date]
        df['Sizes'] = df['Mean'].apply(lambda x: 0.25 * x)
        return df
    else:
        print('Pickle %s not found' % pickle_file)


def get_cube_source(data_info=None, inds=[0]):
    data_folder = os.path.join(data_info['data_proc_dir'], data_info['process_region'])
    data_file = os.path.join(data_folder,
                             'precip_mean_' + data_info['data_prefix'] + '%s_%s.nc' % (date_select.value,
                                                                                         hour_select.value))
    print(data_file)
    if os.path.exists(data_file):
        cubes = iris.load_cube(data_file)
        xinds = list(set(inds))
        cube = cubes[xinds].collapsed('time', iris.analysis.MEAN)
        lats = cube.coord('latitude').points
        lons = cube.coord('longitude').points

        return cube, lats, lons
    else:
        print('%s not found' %data_file)
        pass


data_infos = model_info_dicts()
menu_data = get_menu_data(data_info=data_infos[-1])
menu_data['hours'] = ['00', '00']
print(menu_data)
date_select = Select(value=menu_data['dates'][1], title='Date:', options=menu_data['dates'])
hour_select = Select(value=menu_data['hours'][1], title='Hour:', options=menu_data['hours'])
# date_select.value = '20220401'
# hour_select.value = '00'

# cube_source = ColumnDataSource(data={'image':[None]})
# centroid_df = pd.DataFrame({'TimeInds': [], 'clon': [], 'clat': [], 'rad': []})
# source_centroid = ColumnDataSource(data=centroid_df)

tabs = []
rs = []

with open(os.path.join(os.path.dirname(__file__), 'data/countries.geo.json'), 'r') as f:
    countries = GeoJSONDataSource(geojson=f.read())

# for data_info in data_infos:

cube, lats, lons = get_cube_source(data_info=data_infos[0])
cube_source = ColumnDataSource(data={'image': [cube.data], 'map_label': ['%s_%s' % (date_select.value,
                                                                                    hour_select.value)]})

# A small df for the mouse selection
centroid_df = pd.DataFrame({'TimeInds': [0], 'clon': [0], 'clat': [0], 'rad': [0]})
#cir_df = pd.DataFrame({'obj_lons': flatten_list(obj_lons), 'obj_lats': flatten_list(obj_lats)})

# cube_source.data.update(data={'image': [cube.data]})  # OK

minlat, maxlat = min(lats), max(lats)
minlon, maxlon = min(lons), max(lons)

df = get_pkl_data(date_select.value, hour_select.value, data_info=data_infos[0])

source_df = ColumnDataSource(data=df)
source_centroid = ColumnDataSource(data=centroid_df)
# source_centroid.data.update(centroid_df)

TOOLTIPS = [(tab_name, "@" + tab_name) for tab_name in ['DateLabel','TimeInds', 'Forecast_period',
                                                        'Forecast_reference_time',
                                                        'Threshold', 'ObjectLabel', 'Area',
                                                        'Perimeter', 'Eccentricity',
                                                        'Orientation', 'Mean', 'Std', 'Max',
                                                        'Min', 'Centroid']]
TOOLS = "pan,wheel_zoom,reset,hover,save, lasso_select, box_select"
p1 = figure(width=500, height=500, title="", tools=TOOLS, tooltips=TOOLTIPS)
p1.xaxis.axis_label = "Area (grid points)"
p1.yaxis.axis_label = "Max (mm/3hr)"
p1.background_fill_color = "#fafafa"
p1.select(BoxSelectTool).select_every_mousemove = False
p1.select(LassoSelectTool).select_every_mousemove = False
r = p1.scatter(x="Area", y="Max", size="Sizes", source=source_df, line_color=None, fill_alpha=0.6)
# rs = rs.append(r)

p2 = figure(plot_width=800, plot_height=500, title='',
            tools=["pan, reset, save, box_zoom, wheel_zoom, hover"],
            x_axis_label='Longitude', y_axis_label='Latitude')
color_mapper = LinearColorMapper(palette=Viridis6, low=0, high=50)
p2.image("image", source=cube_source, x=minlon, y=minlat, dw=maxlon - minlon,
         dh=maxlat - minlat, color_mapper=color_mapper, alpha=0.7)
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12,
                     border_line_color=None, location=(0, 0),
                     orientation='horizontal')
p2.add_layout(color_bar, 'below')
p2.patches("xs", "ys", color=None, line_color="black", source=countries)
# p2.circle(x="obj_lons", y="obj_lats", size=10,  line_color="white", alpha=0.5, fill_alpha=0, hover_color='white', source=cir_df)
p2.circle(x="clon", y="clat", radius="rad", line_color="white", fill_alpha=0., radius_units='data',
          hover_color='white', source=source_centroid)
p2.x_range = Range1d(start=minlon, end=maxlon)
p2.y_range = Range1d(start=minlat, end=maxlat)

glyph = Text(x=115, y=21, text="map_label", text_color="grey", text_align='center', text_alpha=0.25)
p2.add_glyph(cube_source, glyph)

# tabs.append(Panel(child=row(p1,p2), title=data_info['label']))

# tabs_plots = Tabs(tabs=tabs)
# print(dir(p1.scatter()))
controls = [date_select, hour_select]

inputs = column(*controls, width=150)
# layout = row(controls, tabs_plots)
layout = row(inputs, row(p1, p2))

curdoc().add_root(layout)
curdoc().title = "Selection Histogram"


def update_plot(attr, old, new):
    inds = new
    if not inds:
        inds = [0]
        print('New')
        print(new, inds)
    df = get_pkl_data(date_select.value, hour_select.value, data_info=data_infos[0])
    df['DateLabel'] = [d.strftime("%Y/%m/%d") for d in df.Date]
    r.data_source.data = df

    ddf = df.iloc[list(set(inds))]

    centroid_df = ddf[['Date', 'TimeInds', 'ObjectLabel', 'GridPoints', 'Centroid']]
    centroid_df[['clon', 'clat']] = pd.DataFrame(ddf['Centroid'].tolist(), index=ddf.index)
    centroid_df['rad'] = ddf['Area'].apply(lambda x: 0.15 * np.sqrt(x / np.pi))

    print(centroid_df)
    # cir_df = pd.DataFrame({'obj_lons': flatten_list(obj_lons), 'obj_lats': flatten_list(obj_lats)})
    cube, lats, lons = get_cube_source(data_info=data_infos[0], inds=centroid_df.TimeInds.values)
    cube_source.data.update({'image': [cube.data], 'map_label': ['%s_%s'
                                                            % (date_select.value, hour_select.value)]})
    source_centroid.data = centroid_df


def update_data(attr, old, new):
    print('new Date:'+new)

    df = get_pkl_data(date_select.value, hour_select.value, data_info=data_infos[0])
    df['DateLabel'] = [d.strftime("%Y/%m/%d") for d in df.Date]
    print(df)
    print('DF Index values:')
    xinds = list(set(df.TimeInds.values))
    r.data_source.data = df

    cube, lats, lons = get_cube_source(data_info=data_infos[0], inds=xinds)
    cube_source.data.update({'image': [cube.data], 'map_label': ['%s_%s'
                                                            % (date_select.value, hour_select.value)]})
    #update_plot(attr, old, df.TimeInds.values)
    update_plot(attr, old, xinds)


for control in controls:
    control.on_change('value', update_data)

# for r in rs:
r.data_source.selected.on_change('indices', update_plot)
