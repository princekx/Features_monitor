import numpy as np
import scipy.ndimage as ndimage
from tqdm import tqdm
from skimage import measure
import pandas as pd


def generate_mask(cube_data, threshold, threshold_method):
    '''
    Generate masks based on threshold and threshold method
    e.g. mask precip >= 10 uses threshold=10, threshold_method='geq'
    e.g. mask OLR <= 240 uses threshold=240, threshold_method='leq'
    :param cube_data:
    :type cube_data:
    :param threshold:
    :type threshold:
    :param threshold_method: 'leq' for <= or 'geq' for >=
    :type threshold_method:
    :return:
    :rtype:
    '''
    if threshold_method == 'geq':
        mask = cube_data >= threshold
    elif threshold_method == 'leq':
        mask = cube_data <= threshold
    return mask


def grid_features(cube, thresholds=None, time_index=0, threshold_method='geq'):
    '''
    2D cube tracking for thresholds
    :param cube: Lat-lon cube
    :type cube:
    :param thresholds:
    :type thresholds:
    :param time_index:
    :type time_index:
    :param threshold_method:
    :type threshold_method:
    :return: DataFrame of identified objects and their properties
    :rtype: Pandas DataFrame
    '''
    assert thresholds is not None, "Threshold values not found."

    # indices = []
    time_indices = []
    cube_dates = []
    object_coords = []
    object_labels = []
    threshold_values = []
    areas = []
    perimeters = []
    eccs = []
    orients = []
    centroids = []
    mean_values = []
    std_values = []
    max_values = []
    min_values = []
    ngrid_points = []
    forecast_period = []
    forecast_reference_time = []
    index = time_index
    if cube.ndim == 2:
        ny, nx = cube.shape
        lons, lats = cube.coord('longitude').points, cube.coord('latitude').points

        # Cube date
        if cube.coords('time'):
            cube_date = cube.coord('time').units.num2date(cube.coord('time').points)

        if cube.coords('forecast_reference_time'):
            forecast_rt = cube.coord('forecast_reference_time').units.num2date(
                cube.coord('forecast_reference_time').points)[0]
        else:
            forecast_rt = np.nan

        if cube.coords('forecast_period'):
            forecast_p = cube.coord('forecast_period').points[0]
        else:
            forecast_p = np.nan

        for threshold in thresholds:
            # print('Thresholding %s' %threshold)
            cube_data = cube.data.copy()
            mask = generate_mask(cube_data, threshold, threshold_method)

            # Label each feature in the mask
            labeled_array, num_features = ndimage.measurements.label(mask)
            #print('%s features labelled.' % num_features)
            # labelled_array is a mask hence != operator below
            for feature_num in tqdm(range(1, num_features)):
                # threshold
                threshold_values.append(threshold)
                object_labels.append('%s_%s_%s' % (index, threshold, feature_num))
                loc = labeled_array != feature_num
                data_object = np.ma.masked_array(cube_data, loc)

                ###### Skimage needs the mask reversed
                lab_image = measure.label(labeled_array == feature_num)
                region = measure.regionprops(lab_image, np.ma.masked_array(cube_data, ~loc))

                # perimeter, eccentricity, orientation
                areas.append([p.area for p in region][0])
                perimeters.append([p.perimeter for p in region][0])
                eccs.append([p.eccentricity for p in region][0])
                orients.append([p.orientation for p in region][0])
                # print(eccs)
                ###############

                mean_values.append(np.ma.mean(data_object))
                std_values.append(np.ma.std(data_object))
                max_values.append(np.ma.max(data_object))
                min_values.append(np.ma.min(data_object))

                y, x = ndimage.measurements.center_of_mass(data_object)
                centroids.append((lons[round(x)], lats[round(y)]))

                object_inds = np.where(loc == False)
                object_lats = [lats[i] for i in object_inds[0]]
                object_lons = [lons[i] for i in object_inds[1]]

                object_coords.append([(x, y) for x, y in zip(object_lons, object_lats)])
                ngrid_points.append(len(object_lats))

                cube_dates.append(cube_date)
                forecast_period.append(forecast_p)
                forecast_reference_time.append(forecast_rt)
                # indices.append(index)
                time_indices.append(index)

        index += 1
    features = {'TimeInds': time_indices, 'Date': cube_dates,
                'Forecast_period': forecast_period, 'Forecast_reference_time': forecast_reference_time,
                'Threshold': threshold_values, 'ObjectLabel': object_labels, 'Area': areas, 'GridPoints': ngrid_points,
                'Mean': mean_values, 'Std': std_values,
                'Max': max_values, 'Min': min_values,
                'Centroid': centroids, 'Polygon': object_coords,
                'Perimeter': perimeters, 'Eccentricity': eccs, 'Orientation': orients}

    features = pd.DataFrame(features, columns=['TimeInds', 'Date', 'Forecast_period',
                                               'Forecast_reference_time', 'Threshold', 'ObjectLabel', 'Area',
                                               'Perimeter',
                                               'GridPoints', 'Eccentricity', 'Orientation',
                                               'Mean', 'Std', 'Max', 'Min', 'Centroid', 'Polygon'])
    return features

def grid_features_3d(cubes, thresholds=None, threshold_method='geq'):
    '''
    Returns a DataFrame of detected object properties for various thresholds
    :param cubes:
    :type cubes:
    :param thresholds:
    :type thresholds:
    :param threshold_method:
    :type threshold_method:
    :return:
    :rtype:
    '''
    frames = []
    if len(cubes.shape) == 3:
        ntime, _, _ = cubes.shape
        for i in range(ntime):
            print('%s/%s' %(i, ntime))
            frames.append(grid_features(cubes[i], thresholds=thresholds, time_index=i,
                                        threshold_method=threshold_method))
    else:
        frames.append(grid_features(cubes, thresholds=thresholds, time_index=0,
                                    threshold_method=threshold_method))
    return pd.concat(frames, ignore_index=True)