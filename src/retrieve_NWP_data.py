import os
import sys
import datetime
import numpy as np

def retrieve_nwp_3hr_data(date, hour, lead, moosedir=None):
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
    remote_data_dir = '/scratch/hadpx/Feature_monitor_data/'
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

def retrieve_nwp_forecast_data(date, runid=None, moosedir=None):
    str_year, str_month, str_day = str(date.year), str('%02d' % date.month), str('%02d' % date.day)

    date_label = '%s%s%s' % (str_year, str_month, str_day)
    print('Doing date : %s' % date_label)
    query_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queryfiles')

    print(query_files_dir)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!! BUG ALERT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Bug in MOGREPS data archival. It only archives 12 members. 
    # Correct this once the full 36 members are available on moose.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # This is the correct path for prod run

    # Use this for temporary use for PS39 bug
    # moosedir = data_paths.dirs('mog_moose_dir')# + '%s%s.pp' % (str_year, str_month)

    hr_list = [00]
    fc_times = np.arange(0, 150, 6)  # 15 days
    print(fc_times)

    # Loop over hour

    for hr in hr_list:
        remote_data_dir = os.path.join('/scratch/hadpx/Feature_montor_data/%s/%s/%s/%s/%s' % (runid,
                                                                                              str_year, str_month,
                                                                                              str_day,
                                                                                              str('%02d' % hr)))

        if not os.path.exists(remote_data_dir):
            print('Making dir: %s' % remote_data_dir)
            os.makedirs(remote_data_dir)
            # os.system('ls %s' %remote_data_dir)

        # os.system('moo ls %s' %file_moose)
        precip_query_file = os.path.join(query_files_dir, 'mogg_query_precip')
        local_query_file1 = os.path.join(query_files_dir, 'local_query1')

        hr_str = str('%02d' % hr)
        # check if the directory is empty
        for fc in fc_times:
            fc_3d = str('%03d' % fc)
            print('Forecast is %s ' % fc)
            # filemoose = 'prods_op_mogreps-g_%s%s%s_%s_%s_%s.pp' % (str_year, str_month, str_day, hr, digit2_mem, fct)
            # filemoose_pb = '%s%s%sT%s00Z_pb_t%s.pp' % (str_year, str_month, str_day, hr_str, fc_3d)
            filemoose_pb = '%s%s%sT%s00Z_glm_t%s.ff' % (str_year, str_month, str_day, hr_str, fc_3d)
            outfile = 'englaa_pb%s.pp' % fc_3d
            file_moose_pb = os.path.join(moosedir, filemoose_pb)
            print(file_moose_pb)
            try:
                # Replace the fctime and filemoose in query file
                replacements = {'fctime': str(fc), 'filemoose_pb': filemoose_pb}

                with open(precip_query_file) as query_infile, open(local_query_file1, 'w') as query_outfile:
                    for line in query_infile:
                        for src, target in replacements.items():
                            line = line.replace(src, target)
                        query_outfile.write(line)

                # do the retrieval
                remote_data_dir_outfile = '%s/%s' % (remote_data_dir, outfile)

                if not os.path.exists(remote_data_dir_outfile):
                    command = '/opt/moose-client-wrapper/bin/moo select %s %s %s' % (local_query_file1,
                                                                                     moosedir,
                                                                                     remote_data_dir_outfile)
                    print(command)
                    os.system(command)
                else:
                    print('%s found. Skipping retrieval...' % remote_data_dir_outfile)
            except:
                print('%s not returned. Check file on moose' % file_moose)
                sys.exit()

    else:
        print('%s has files. Skipping retrieval...' % remote_data_dir)


if __name__ == '__main__':
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday = datetime.date(2022,3,29)
    moosedir = 'moose:/opfc/atm/global/prods/'
    retrieve_nwp_3hr_data(yesterday, hour='06', lead='003', moosedir=moosedir)
