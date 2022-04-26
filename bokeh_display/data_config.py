def model_info_dicts():
    oper = dict()
    oper['label'] = 'OPER_UM'
    oper['source'] = 'moose:/opfc/atm/global/prods/'
    oper['data_prefix'] = 'prods_op_gl-mn_'
    oper['plot_feature_dir'] = '/scratch/hadpx/Feature_monitor_data/features/'+oper['label']
    oper['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/global_um'
    oper['process_region'] = 'SEAsia'
    oper['region_lat_range'] = (-10, 20)
    oper['region_lon_range'] = (90, 140)

    ps45 = dict()
    ps45['label'] = 'PS45'
    ps45['source'] = 'moose:/opfc/atm/global/prods/psuite45.pp'
    ps45['data_prefix'] = 'prods_op_gl-mn_'
    ps45['plot_feature_dir'] = '/scratch/hadpx/Feature_monitor_data/features/' + ps45['label']
    ps45['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/global_um_ps45'
    ps45['process_region'] = 'SEAsia'
    ps45['region_lat_range'] = (-10, 20)
    ps45['region_lon_range'] = (90, 140)

    obs = dict()
    obs['label'] = 'GPM_Imerge'
    obs['source'] = '/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/NRTearly/1hr-accum'
    obs['data_prefix'] = 'gpm_imerg_NRTearly_'
    obs['plot_feature_dir'] = '/scratch/hadpx/Feature_monitor_data/features/' + obs['label']
    obs['data_proc_dir'] = '/scratch/hadpx/Feature_monitor_data/gpm'
    obs['process_region'] = 'SEAsia'
    obs['region_lat_range'] = (-10, 20)
    obs['region_lon_range'] = (90, 140)

    #return [oper, ps45, obs]
    return [obs]