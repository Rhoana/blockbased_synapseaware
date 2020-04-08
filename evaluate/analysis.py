import os



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPickledData, ReadPtsFile



def EvaluateSkeletons(prefix):
    data = ReadMetaData(prefix)

    # read in statistics about this data set
    statistics_directory = '{}/statistics'.format(data.TempDirectory())
    statistics_filename = '{}/combined-statistics.pickle'.format(statistics_directory)
    statistics = ReadPickledData(statistics_filename)

    label_volumes = statistics['label_volumes']

    total_volume = 0
    total_thinned_skeleton_length = 0
    total_refined_skeleton_length = 0

    for label in label_volumes:
        # read pre-refinement skeleton
        thinning_filename = '{}/skeletons/{:016d}.pts'.format(data.TempDirectory(), label)

        # skip files that do not exist (no synapses, e.g.)
        if not os.path.exists(thinning_filename): continue

        thinned_skeletons_global_pts, _ = ReadPtsFile(data, thinning_filename)
        thinned_skeletons = thinned_skeletons_global_pts[label]

        refined_filename = '{}/skeletons/{:016d}.pts'.format(data.SkeletonOutputDirectory(), label)

        refined_skeletons_global_pts, _ = ReadPtsFile(data, refined_filename)
        refined_skeletons = refined_skeletons_global_pts[label]

        # get the volume and total remaining voxels
        volume = label_volumes[label]
        thinned_skeleton_length = len(thinned_skeletons)
        refined_skeleton_length = len(refined_skeletons)

        # update the variables that aggregate all labels
        total_volume += volume
        total_thinned_skeleton_length += thinned_skeleton_length
        total_refined_skeleton_length += refined_skeleton_length

        # calculate the percent and reduction of total voxels remaining
        thinned_remaining_percent = 100 * thinned_skeleton_length / volume
        thinning_reduction_factor = volume / thinned_skeleton_length
        refined_remaining_percent = 100 * refined_skeleton_length / thinned_skeleton_length
        refinement_reduction_factor = thinned_skeleton_length / refined_skeleton_length

        # caluclate the total percent/reduction after all steps
        total_skeleton_percent = 100 * refined_skeleton_length / volume
        total_skeleton_reduction = volume / refined_skeleton_length

        print ('Label: {}'.format(label))
        print ('  Input Volume:           {:10d}'.format(volume))
        print ('  Topological Thinning:   {:10d}    ({:05.2f}%)  {:9.2f}x'.format(thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
        print ('  Skeleton Refinement:    {:10d}    ({:05.2f}%)  {:9.2f}x'.format(refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
        print ('  Total:                                ({:05.2f}%)  {:9.2f}x'.format(total_skeleton_percent, total_skeleton_reduction))

    # calculate the percent and reduction of total voxels remaining
    thinned_remaining_percent = 100 * total_thinned_skeleton_length / total_volume
    thinning_reduction_factor = total_volume / total_thinned_skeleton_length
    refined_remaining_percent = 100 * total_refined_skeleton_length / total_thinned_skeleton_length
    refinement_reduction_factor = total_thinned_skeleton_length / total_refined_skeleton_length

    # caluclate the total percent/reduction after all steps
    total_skeleton_percent = 100 * total_refined_skeleton_length / total_volume
    total_skeleton_reduction = total_volume / total_refined_skeleton_length

    print ('Input Volume:           {:10d}'.format(total_volume))
    print ('Topological Thinning:   {:10d}    ({:05.2f}%)  {:9.2f}x'.format(total_thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
    print ('Skeleton Refinement:    {:10d}    ({:05.2f}%)  {:9.2f}x'.format(total_refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
    print ('Total:                                ({:05.2f}%)  {:9.2f}x'.format(total_skeleton_percent, total_skeleton_reduction))
