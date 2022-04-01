import datetime
import src.retrieve_NWP_data as process_data
if __name__ == '__main__':

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    yesterday = datetime.date(2022,3,21)
    moosedir = 'moose:/opfc/atm/global/prods/'
    model_data_dir = '/scratch/hadpx/Feature_monitor_data/global_um'
    leads = range(0, 69, 3)

    lead_times = [str('%03d' % l) for l in leads]

    for lead_time in lead_times:
        process_data.retrieve_nwp_3hr_data(yesterday, hour='06', lead=lead_time,
                              moosedir=moosedir, remote_data_dir=model_data_dir)

        obs_data_dir = '/scratch/hadpx/Feature_monitor_data/gpm'
        process_data.retrieve_gpm_from_modelTimeBounds(yesterday, hour='06', lead=lead_time,
                                          model_data_dir=model_data_dir)

    process_data.construct_3hrly_from_accumm(yesterday, hour='06', model_data_dir=model_data_dir)