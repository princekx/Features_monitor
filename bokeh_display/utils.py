import bokeh
import pandas as pd
import datetime
import os
import numpy as np
import glob

def get_menu_data(data_info=None):
    '''
    Returns the available dates and hours to generate menu items in Bokeh
    Also return the labels and region info in the dictionary
    :param data_info:
    :type data_info: dictionary
    :return: menu_data
    :rtype: dictionary
    '''
    data_dir = os.path.join(data_info['data_proc_dir'], data_info['process_region'])
    pkl_files = glob.glob(os.path.join(data_dir,'*.pkl'))
    menu_data = {}
    menu_data['hours'] = list(set([pkl.split('_')[-1].split('.')[0] for pkl in pkl_files]))
    menu_data['dates'] = list(set([pkl.split('_')[-2] for pkl in pkl_files]))
    menu_data['label'] = data_info['label']
    menu_data['region_lat_range'] = data_info['region_lat_range']
    menu_data['region_lon_range'] = data_info['region_lon_range']
    return menu_data