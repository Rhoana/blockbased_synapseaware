import os
import time



import numpy as np



from blockbased_synapseaware.utilities.dataIO import PickleData, ReadH5File, ReadMetaData, ReadPickledData



def BlockStatistics(seg):
    # calculate the number of non zero voxels and labels in this volume
    n_non_zero = np.count_nonzero(seg)
    labels, counts = np.unique(seg, return_counts=True)

    # if there is background component, ignore
    if not labels[0]:
        labels = labels[1:]
        counts = counts[1:]

    nlabels = len(labels)

    # keep track of the voxel counts for each label
    voxel_counts = {}
    for iv in range(nlabels):
        voxel_counts[labels[iv]] = counts[iv]

    return n_non_zero, nlabels, voxel_counts



def CalculatePerBlockStatistics(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # create the output directory if it exists
    statistics_directory = '{}/statistics'.format(data.TempDirectory())
    if not os.path.exists(statistics_directory):
        os.makedirs(statistics_directory, exist_ok=True)

    # calculate raw block statistics
    raw_seg = data.ReadRawSegmentationBlock(iz, iy, ix)
    raw_n_non_zero, raw_nlabels, raw_voxel_counts = BlockStatistics(raw_seg)
    del raw_seg
    # calculate filled block statistics
    seg = data.ReadSegmentationBlock(iz, iy, ix)
    filled_n_non_zero, filled_nlabels, filled_voxel_counts = BlockStatistics(seg)
    del seg
    
    assert (filled_nlabels == raw_nlabels)

    nfilled_voxels = filled_n_non_zero - raw_n_non_zero

    # create a dictionary for saving
    statistics = {}

    statistics['nlabels'] = raw_nlabels
    statistics['raw_n_non_zero'] = raw_n_non_zero
    statistics['raw_voxel_counts'] = raw_voxel_counts
    statistics['filled_n_non_zero'] = filled_n_non_zero
    statistics['filled_voxel_counts'] = filled_voxel_counts

    statistics_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pickle'.format(statistics_directory, iz, iy, ix)
    PickleData(statistics, statistics_filename)

    total_time = time.time() - total_time

    print ('Total Time: {:0.2f} seconds.'.format(total_time))



def CombineStatistics(data):
    # start timing statistics
    total_time = time.time()

    # the statistics directory must already exist for previous results
    statistics_directory = '{}/statistics'.format(data.TempDirectory())

    label_volumes_with_holes = {}
    label_volumes_filled = {}
    label_volumes = {}
    neuronal_volume_with_holes = 0
    neuronal_volume = 0

    # read the pickle file generated for each block
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                statistics_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pickle'.format(statistics_directory, iz, iy, ix)
                statistics = ReadPickledData(statistics_filename)

                for label in statistics['raw_voxel_counts'].keys():
                    if not label in label_volumes_with_holes:
                        label_volumes_with_holes[label] = 0
                        label_volumes[label] = 0

                    label_volumes_with_holes[label] += statistics['raw_voxel_counts'][label]
                    label_volumes[label] += statistics['filled_voxel_counts'][label]

                neuronal_volume_with_holes += statistics['raw_n_non_zero']
                neuronal_volume += statistics['filled_n_non_zero']

    labels = label_volumes.keys()
    for label in labels:
        label_volume = label_volumes[label]
        label_volume_filled = label_volume - label_volumes_with_holes[label]

        print ('Label {}:'.format(label))
        print ('  Volume:        {:14d}'.format(label_volume))
        print ('  Filled Volume: {:14d}   ({:5.2f}%)\n'.format(label_volume_filled, 100 * label_volume_filled / label_volume))

        # add to dictionary of filled volues

        label_volumes_filled[label] = label_volume_filled
    # calculate what percent of the total volume of holes were filled
    neuronal_volume_filled = neuronal_volume - neuronal_volume_with_holes
    total_volume = data.NVoxels()

    print ('Volume Size:     {:14d}'.format(total_volume))
    print ('  Neuron Volume: {:14d}   ({:5.2f}%)'.format(neuronal_volume, 100 * neuronal_volume / total_volume))
    print ('  Filled Volume: {:14d}   ({:5.2f}%)'.format(neuronal_volume_filled, 100 * neuronal_volume_filled / neuronal_volume))

    # output the aggregated data to a pickle file
    statistics = {}

    statistics['label_volumes'] = label_volumes
    statistics['label_volumes_with_holes'] = label_volumes_with_holes
    statistics['label_volumes_filled'] = label_volumes_filled

    statistics['neuronal_volume'] = neuronal_volume
    statistics['neuronal_volume_with_holes'] = neuronal_volume_with_holes
    statistics['neuronal_volumes_filled'] = neuronal_volume_filled

    statistics_filename = '{}/combined-statistics.pickle'.format(statistics_directory)
    PickleData(statistics, statistics_filename)

    total_time = time.time() - total_time

    print ('Total Time: {:0.2f} seconds.'.format(total_time))



def CalculateBlockStatisticsSequentially(meta_filename):
    data = ReadMetaData(meta_filename)

    # iterate over all blocks
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                CalculatePerBlockStatistics(data, iz, iy, ix)

    CombineStatistics(data)
