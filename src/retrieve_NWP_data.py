import os
import sys
import datetime
import iris
from iris.time import PartialDateTime
import glob


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


def retrieve_gpm_from_modelTimeBounds(date, hour=None, lead=None, model_data_dir=None,
                                      gpm_folder='/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/NRTearly/1hr-accum',
                                      gpm_out_folder='/scratch/hadpx/Feature_monitor_data/gpm'):
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
    moose_file_name = 'prods_op_gl-mn_%s_%s_%s.pp' % (date_label, hour, lead)
    remote_data_dir_outfile = os.path.join(model_data_dir, moose_file_name)
    model_cube = iris.load_cube(remote_data_dir_outfile)
    m_time_coord = model_cube.coord('time')
    m_time_bounds = model_cube.coord('time').bounds
    #m_cube_times = [m_time_coord.units.num2date(tp) for tp in m_time_coord.points]

    # m_time_bounds as datetime objects from model
    #time_delta = m_time_bounds[1] - m_time_bounds[0]
    # time delta in hours to choose 3 hourly or 6 hourly mean GPM data
    #time_delta = time_delta.seconds / 60 / 60.
    #gpm_folder = os.path.join(gpm_folder, '%shr-accum' % str(int(time_delta)))
    #
    # read GPM data
    file_name = glob.glob(gpm_folder + '/*.nc')[0]
    print(file_name)
    obs_cube = iris.load_cube(file_name, 'm01s05i216')

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
    # Constrain the time
    gpm_time_constraint = iris.Constraint(time=lambda cell: pdt1 <= cell.point < pdt2)
    obs_cube = obs_cube.extract(gpm_time_constraint)

    if len(obs_cube.shape) == 3:
        obs_cube = obs_cube.collapsed('time', iris.analysis.SUM)

    # extracting SEAsia
    model_cube = model_cube.intersection(latitude=(-20, 30), longitude=(100, 130))
    obs_cube = obs_cube.intersection(latitude=(-20, 30), longitude=(100, 130))

    # regridding obs to model grid
    obs_cube = regrid_cube(obs_cube, model_cube)

    obs_outfile = os.path.join(gpm_out_folder, 'gpm_%s_%s_%s.nc' %(date_label, hour, lead))
    #return obs_cube


def retrieve_nwp_3hr_data(date, hour=None, lead=None, moosedir=None, remote_data_dir=None):
    '''
    Retrieve NWP global 3hourly data

    :param date:
    :type date:
    :param hour:
    :type hour:
    :param lead:
    :type lead:
    :param moosedir:
    :type moosedir:
    :return:
    :rtype:
    '''
    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)

    date_label = '%s%s%s' % (str_year, str_month, str_day)
    print('Doing date : %s' % date_label)
    query_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queryfiles')

    print(query_files_dir)

    if not os.path.exists(remote_data_dir):
        print('Making dir: %s' % remote_data_dir)
        os.makedirs(remote_data_dir)

    all_query_file = os.path.join(query_files_dir, 'nwp_query_all')
    local_query_file1 = os.path.join(query_files_dir, 'local_query1')
    moose_file_name = 'prods_op_gl-mn_%s_%s_%s.pp' %(date_label, hour, lead)
    dir_moose = os.path.join(moosedir, '%s.pp'%str_year)
    print(moose_file_name)
    #os.system('moo ls %s' % filemoose)

    # Replace the fctime and filemoose in query file
    replacements = {'filemoose_pb': moose_file_name}

    with open(all_query_file) as query_infile, open(local_query_file1, 'w') as query_outfile:
        for line in query_infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
                print(line)
            query_outfile.write(line)

    print(local_query_file1)
    # do the retrieval
    remote_data_dir_outfile = os.path.join(remote_data_dir, moose_file_name)

    if not os.path.exists(remote_data_dir_outfile):
        command = '/opt/moose-client-wrapper/bin/moo select %s %s %s' % (local_query_file1,
                                                                         dir_moose,
                                                                         remote_data_dir_outfile)
        print(command)
        os.system(command)



if __name__ == '__main__':
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday = datetime.date(2022,3,29)
    moosedir = 'moose:/opfc/atm/global/prods/'
    model_data_dir = '/scratch/hadpx/Feature_monitor_data/global_um'

    retrieve_nwp_3hr_data(yesterday, hour='06', lead='009',
                          moosedir=moosedir, remote_data_dir=model_data_dir)

    obs_data_dir = '/scratch/hadpx/Feature_monitor_data/gpm'
    retrieve_gpm_from_modelTimeBounds(yesterday, hour='06', lead='009', model_data_dir=obs_data_dir)
