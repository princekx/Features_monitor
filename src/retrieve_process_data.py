import os
import sys
import datetime
import iris
from iris.time import PartialDateTime
import numpy as np
import glob
import warnings
import iris.quickplot as qplt
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

def regrid_cube(my_cubes, base_cube):
    base_cube.coord('latitude').units = my_cubes.coord('latitude').units = 'degrees'
    base_cube.coord('longitude').units = my_cubes.coord('longitude').units = 'degrees'

    base_cube.coord('latitude').coord_system = None
    base_cube.coord('longitude').coord_system = None
    my_cubes.coord('latitude').coord_system = None
    my_cubes.coord('longitude').coord_system = None

    # For lat/lon regriding, make sure coordinates have bounds
    if my_cubes.coord('longitude').bounds is None:
        my_cubes.coord('longitude').guess_bounds()
    if my_cubes.coord('latitude').bounds is None:
        my_cubes.coord('latitude').guess_bounds()
    if base_cube.coord('longitude').bounds is None:
        base_cube.coord('longitude').guess_bounds()
    if base_cube.coord('latitude').bounds is None:
        base_cube.coord('latitude').guess_bounds()

    #reg_cube = iris.experimental.regrid.regrid_area_weighted_rectilinear_src_and_grid(my_cubes, \
    #                                                                                  base_cube, mdtol=0)
    reg_cube = my_cubes.regrid(base_cube, iris.analysis.Linear())
    return reg_cube

def construct_3hrly_from_accumm(date, hour=None, model_data_info=None, obs_data_info=None):
    '''

    :param date:
    :type date:
    :param hour:
    :type hour:
    :param model_data_dir:
    :type model_data_dir:
    :param gpm_folder:
    :type gpm_folder:
    :param gpm_out_folder:
    :type gpm_out_folder:
    :return:
    :rtype:
    '''
    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)
    date_label = '%s%s%s' % (str_year, str_month, str_day)



    # read the model data
    ##########################################################################
    model_files = glob.glob(os.path.join(model_data_info['data_proc_dir'], model_data_info['process_region'],
                                         model_data_info['data_prefix']+'%s_%s_*.nc' % (date_label, hour)))
    model_cube = iris.load_cube(model_files, 'm01s05i226')
    model_diff_cube = model_cube.copy()
    model_diff_cube.data[1:] = np.diff(model_cube.data, axis=0)
    model_mean_file = os.path.join(model_data_info['data_proc_dir'], model_data_info['process_region'],
                                         'precip_mean_'+model_data_info['data_prefix']+'%s_%s.nc' % (date_label, hour))
    iris.save(model_diff_cube, model_mean_file)
    print('Written %s .' %model_mean_file)

    # read the GPM data
    ##########################################################################
    # remote_data_dir_outfile = os.path.join(model_data_dir, moose_file_name)
    print(os.path.join(obs_data_info['data_proc_dir'], obs_data_info['process_region'],
                                         obs_data_info['data_prefix']+'%s_%s_*.nc' % (date_label, hour)))

    obs_files = glob.glob(os.path.join(obs_data_info['data_proc_dir'], obs_data_info['process_region'],
                                         obs_data_info['data_prefix']+'%s_%s_*.nc' % (date_label, hour)))
    print(obs_files)
    obs_cube = iris.load_cube(obs_files, 'm01s05i216')
    obs_diff_cube = obs_cube.copy()
    obs_diff_cube.data[1:] = np.diff(obs_cube.data, axis=0)
    obs_mean_file = os.path.join(obs_data_info['data_proc_dir'], obs_data_info['process_region'],
                                   'precip_mean_'+obs_data_info['data_prefix']+'%s_%s.nc' % (date_label, hour))
    iris.save(obs_diff_cube, obs_mean_file)
    print('Written %s .' % obs_mean_file)

def retrieve_gpm_from_modelTimeBounds(date, hour=None, lead=None,
                                      model_data_info=None, obs_data_info=None):
    '''
    Generate the GPM data to match the model data
    :param date:
    :type date:
    :param hour:
    :type hour:
    :param lead:
    :type lead:
    :param model_data_dir:
    :type model_data_dir:
    :param gpm_folder:
    :type gpm_folder:
    :return:
    :rtype:

    '''
    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)
    date_label = '%s%s%s' % (str_year, str_month, str_day)

    # read the model data
    ##########################################################################
    moose_file_name = model_data_info['data_prefix'] + '%s_%s_%s.pp' % (date_label, hour, lead)
    remote_data_dir_outfile = os.path.join(model_data_info['data_proc_dir'], moose_file_name)

    data_proc_dir = obs_data_info['data_proc_dir']
    if not os.path.exists(data_proc_dir):
        print('Making dir: %s' % data_proc_dir)
        os.makedirs(data_proc_dir)

    data_proc_reg_dir = os.path.join(data_proc_dir, obs_data_info['process_region'])
    if not os.path.exists(data_proc_reg_dir):
        print('Making dir: %s' % data_proc_reg_dir)
        os.makedirs(data_proc_reg_dir)


    model_cube = iris.load_cube(remote_data_dir_outfile)
    m_time_coord = model_cube.coord('time')
    m_time_coord_bounds = model_cube.coord('time').bounds
    m_time_bounds = [m_time_coord.units.num2date(tp) for tp in m_time_coord_bounds][0]
    print(m_time_bounds)

    # extracting SEAsia
    model_cube = model_cube.intersection(latitude=model_data_info['region_lat_range'],
                                         longitude=model_data_info['region_lon_range'])
    # save model to the subset folder
    model_outfile = os.path.join(model_data_info['data_proc_dir'],
                                 model_data_info['process_region'],
                                 model_data_info['data_prefix']+'%s_%s_%s.nc' % (date_label, hour, lead))
    iris.save(model_cube, model_outfile)
    print('Written %s .' % model_outfile)

    #m_cube_times = [m_time_coord.units.num2date(tp) for tp in m_time_coord.points]

    # m_time_bounds as datetime objects from model
    #time_delta = m_time_bounds[1] - m_time_bounds[0]
    # time delta in hours to choose 3 hourly or 6 hourly mean GPM data
    #time_delta = time_delta.seconds / 60 / 60.
    #gpm_folder = os.path.join(gpm_folder, '%shr-accum' % str(int(time_delta)))
    #
    # read GPM data
    file_name = glob.glob(obs_data_info['source'] + '/*.nc')[0]
    print(file_name)

    # Check if the GPM file has been updated at least 5 mins ago
    modTimesinceEpoc = os.path.getmtime(file_name)
    time_since_update = datetime.datetime.now() - datetime.datetime.fromtimestamp(modTimesinceEpoc)

    print('GPM file updated %s mins ago' %(time_since_update.seconds/60))
    if time_since_update.seconds/60. >= 5:

        obs_cube = iris.load_cube(file_name, 'm01s05i216')
        if obs_cube.coords('am_or_pm'):
            obs_cube.remove_coord('am_or_pm')

        #print(obs_cube)
        # now make a time constraint on gpm based on model data bounds
        pdt1 = PartialDateTime(year=m_time_bounds[0].year,
                               month=m_time_bounds[0].month,
                               day=m_time_bounds[0].day,
                               hour=m_time_bounds[0].hour)
        pdt2 = PartialDateTime(year=m_time_bounds[1].year,
                               month=m_time_bounds[1].month,
                               day=m_time_bounds[1].day,
                               hour=m_time_bounds[1].hour)
        print(pdt1, pdt2)
        try:
            # Constrain the time
            gpm_time_constraint = iris.Constraint(time=lambda cell: pdt1 <= cell.point < pdt2)
            obs_cube = obs_cube.extract(gpm_time_constraint)


            print(len(obs_cube.shape))
            if len(obs_cube.shape) == 3:
                obs_cube = obs_cube.collapsed('time', iris.analysis.SUM)

            obs_cube.coord('time').bounds = m_time_coord_bounds
            print(m_time_bounds)

            obs_cube = obs_cube.intersection(latitude=obs_data_info['region_lat_range'],
                                             longitude=obs_data_info['region_lon_range'])

            # regridding obs to model grid
            obs_cube = regrid_cube(obs_cube, model_cube)

            # save gpm to the subset folder
            obs_outfile = os.path.join(obs_data_info['data_proc_dir'],
                                       obs_data_info['process_region'],
                                       obs_data_info['data_prefix']+'%s_%s_%s.nc' %(date_label, hour, lead))
            iris.save(obs_cube, obs_outfile)
            print('Written %s' % obs_outfile)
        except:
            print('Model date/time are beyond the observations. Skip.')
            pass
    else:
        print('GPM data is probably being downloaded. Try again later.')
        print('Check the size of %s' %file_name)
        pass

def retrieve_nwp_3hr_data(date, hour=None, lead=None, data_info=None):
    '''
    Retrieve NWP global 3hourly data
    :param data_info:
    :type data_info:
    :param date:
    :type date:
    :param hour:
    :type hour:
    :param lead:
    :type lead:
    :param info:
    :type info:
    :return:
    :rtype:
    '''

    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)

    date_label = '%s%s%s' % (str_year, str_month, str_day)
    print('Doing date : %s' % date_label)
    query_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queryfiles')

    #print(query_files_dir)

    data_proc_dir = data_info['data_proc_dir']
    if not os.path.exists(data_proc_dir):
        print('Making dir: %s' % data_proc_dir)
        os.makedirs(data_proc_dir)

    data_proc_reg_dir = os.path.join(data_proc_dir, data_info['process_region'])
    if not os.path.exists(data_proc_reg_dir):
        print('Making dir: %s' % data_proc_reg_dir)
        os.makedirs(data_proc_reg_dir)

    all_query_file = os.path.join(query_files_dir, 'nwp_query_all')
    local_query_file1 = os.path.join(query_files_dir, 'local_query1')
    moose_file_name = data_info['data_prefix']+'%s_%s_%s.pp' %(date_label, hour, lead)

    # If PS45 then the moose files does not have a year.pp folder
    if data_info['label'] != 'PS45':
        dir_moose = os.path.join(data_info['source'], '%s.pp' % str_year)
    else:
        dir_moose = os.path.join(data_info['source'])
    #print(moose_file_name)
    #os.system('moo ls %s' % filemoose)

    # Replace the fctime and filemoose in query file
    replacements = {'filemoose_pb': moose_file_name}

    with open(all_query_file) as query_infile, open(local_query_file1, 'w') as query_outfile:
        for line in query_infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            query_outfile.write(line)

    #print(local_query_file1)
    # do the retrieval
    remote_data_dir_outfile = os.path.join(data_proc_dir, moose_file_name)

    if not os.path.exists(remote_data_dir_outfile):
        command = '/opt/moose-client-wrapper/bin/moo select %s %s %s' % (local_query_file1,
                                                                         dir_moose,
                                                                         remote_data_dir_outfile)
        print(command)
        os.system(command)



if __name__ == '__main__':
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday = datetime.date(2022,3,21)
    moosedir = 'moose:/opfc/atm/global/prods/'
    model_data_dir = '/scratch/hadpx/Feature_monitor_data/global_um'
    leads = range(0, 69, 3)

    lead_times = [str('%03d' % l) for l in leads]
    '''
    for lead_time in lead_times:
        retrieve_nwp_3hr_data(yesterday, hour='06', lead=lead_time,
                              moosedir=moosedir, remote_data_dir=model_data_dir)

        obs_data_dir = '/scratch/hadpx/Feature_monitor_data/gpm'
        retrieve_gpm_from_modelTimeBounds(yesterday, hour='06', lead=lead_time,
                                          model_data_dir=model_data_dir)

    '''
    construct_3hrly_from_accumm(yesterday, hour='06', model_data_dir=model_data_dir)