import os
import datetime
import iris
import numpy as np
import src.retrieve_process_data as process_data
import src.grid_features as gf

def compute_features(date, hour='00', thresholds=[10], data_info=None, threshold_method='geq'):
    '''

    :param date:
    :type date:
    :param hour:
    :type hour:
    :param thresholds:
    :type thresholds:
    :param data_info:
    :type data_info:
    :param threshold_method:
    :type threshold_method:
    :return:
    :rtype:
    '''
    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)
    date_label = '%s%s%s' % (str_year, str_month, str_day)

    data_folder = os.path.join(data_info['data_proc_dir'], data_info['process_region'])
    data_file = os.path.join(data_folder,
                             'precip_mean_'+data_info['data_prefix']+'%s_%s.nc' % (date_label, hour))
    print(data_file)
    cube = iris.load_cube(data_file)
    print(cube.data.min())
    print(cube.data.max())
    features = gf.grid_features_3d(cube, thresholds=thresholds,
                                   threshold_method=threshold_method)
    pickle_file = os.path.join(data_folder, 'features_'+data_info['data_prefix']
                              +'%s_%s.pkl' % (date_label, hour))
    features.to_pickle(pickle_file)
    print('Pickled %s' %pickle_file)

if __name__ == '__main__':

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday = datetime.date(2022,4,1)

    oper = dict()
    oper['label'] = 'OPER_UM'
    oper['source'] = 'moose:/opfc/atm/global/prods/'
    oper['data_prefix'] = 'prods_op_gl-mn_'
    oper['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/global_um'
    oper['process_region'] = 'SEAsia'
    oper['region_lat_range'] = (-10, 20)
    oper['region_lon_range'] = (90, 140)
    #moosedir =
    #model_data_dir =

    ps45 = dict()
    ps45['label'] = 'PS45'
    ps45['source'] = 'moose:/opfc/atm/global/prods/psuite45.pp'
    ps45['data_prefix'] = 'prods_op_gl-mn_'
    ps45['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/global_um_ps45'
    ps45['process_region'] = 'SEAsia'
    ps45['region_lat_range'] = (-10, 20)
    ps45['region_lon_range'] = (90, 140)

    obs = dict()
    obs['label'] = 'GPM_Imerge'
    obs['source'] = '/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/NRTearly/1hr-accum'
    obs['data_prefix'] = 'gpm_imerg_NRTearly_'
    obs['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/gpm'
    obs['process_region'] = 'SEAsia'
    obs['region_lat_range'] = (-10, 20)
    obs['region_lon_range'] = (90, 140)

    # Lead times
    leads = range(0, 69, 3)
    lead_times = [str('%03d' % l) for l in leads]

    # List of models to run the codes for with the dictionary definition above
    models = [oper, ps45]

    for hour in ['00', '06', '12', '18']:
        for model in models:
            for lead_time in lead_times:
                process_data.retrieve_nwp_3hr_data(yesterday, hour=hour, lead=lead_time,
                                                   data_info=model)

                process_data.retrieve_gpm_from_modelTimeBounds(yesterday, hour=hour, lead=lead_time,
                                                               model_data_info=model,
                                                               obs_data_info=obs)

            # Now construct 3 hourly totals from accumulations
            # for both models and GPM
            process_data.construct_3hrly_from_accumm(yesterday, hour=hour,
                                                     model_data_info=model,
                                                     obs_data_info=obs)

            # global oper
            compute_features(yesterday, hour=hour, data_info=model)
        # obs
        compute_features(yesterday, hour=hour, data_info=obs)