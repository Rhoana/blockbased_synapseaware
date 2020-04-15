import os
import statistics



import numpy as np
import scipy.spatial



from blockbased_synapseaware.utilities.dataIO import PickleData, ReadAttributePtsFile, ReadMetaData, ReadPickledData, ReadPtsFile
from blockbased_synapseaware.utilities.constants import *



def EvaluateHoleFilling(meta_filename):
    data = ReadMetaData(meta_filename)

    # make sure a results folder is specified
    assert (not data.EvaluationDirectory() == None)

    hole_sizes = {}

    neighbor_label_dicts = {}

    # read in the hole sizes from each block
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                tmp_block_directory = data.TempBlockDirectory(iz, iy, ix)

                # read the saved hole sizes for this block
                hole_sizes_filename = '{}/hole-sizes.pickle'.format(tmp_block_directory)

                holes_sizes_per_block = ReadPickledData(hole_sizes_filename)

                for label in holes_sizes_per_block:
                    hole_sizes[label] = holes_sizes_per_block[label]

                # any value already determined in the local step mush have no neighbors
                associated_label_dict = ReadPickledData('{}/associated-label-set-local.pickle'.format(tmp_block_directory))
                for label in associated_label_dict:
                    neighbor_label_dicts[label] = []

    # read in the neighbor label dictionary that maps values to its neighbors
    tmp_directory = data.TempDirectory()
    neighbor_label_filename = '{}/hole-filling-neighbor-label-dict-global.pickle'.format(tmp_directory)
    neighbor_label_dict_global = ReadPickledData(neighbor_label_filename)
    associated_label_filename = '{}/hole-filling-associated-labels.pickle'.format(tmp_directory)
    associated_label_dict = ReadPickledData(associated_label_filename)

    # make sure that the keys are identical for hole sizes and associated labels (sanity check)
    assert (sorted(hole_sizes.keys()) == sorted(associated_label_dict.keys()))

    # make sure no query component in the global dictionary occurs in the local dictionary
    for label in neighbor_label_dict_global.keys():
        assert (not label in neighbor_label_dicts)

    # create a unified neighbor labels dictionary that combines local and global information
    neighbor_label_dicts.update(neighbor_label_dict_global)

    # make sure that the keys are identical for hole sizes and the neighbor label dicts
    assert (sorted(hole_sizes.keys()) == sorted(neighbor_label_dicts.keys()))

    # union find data structure to link together holes across blocks
    class UnionFindElement:
        def __init__(self, label):
            self.label = label
            self.parent = self
            self.rank = 0

    def Find(element):
        if not element.parent == element:
            element.parent = Find(element.parent)
        return element.parent

    def Union(element_one, element_two):
        root_one = Find(element_one)
        root_two = Find(element_two)

        if root_one == root_two: return

        if root_one.rank < root_two.rank:
            root_one.parent = root_two
        elif root_one.rank > root_two.rank:
            root_two.parent = root_one
        else:
            root_two.parent = root_one
            root_one.rank = root_one.rank + 1

    union_find_elements = {}
    for label in neighbor_label_dicts.keys():
        # skip over elements that remain background
        if not associated_label_dict[label]: continue

        union_find_elements[label] = UnionFindElement(label)

    for label in neighbor_label_dicts.keys():
        # skip over elements that remain background
        if not associated_label_dict[label]: continue

        for neighbor_label in neighbor_label_dicts[label]:
            # skip over the actual neuron label
            if neighbor_label > 0: continue

            # merge these two labels together
            Union(union_find_elements[label], union_find_elements[neighbor_label])

    root_holes_sizes = {}

    # go through all labels in the union find data structure and update the hole size for the parent
    for label in union_find_elements.keys():
        root_label = Find(union_find_elements[label])

        # create this hole if it does not already exist
        if not root_label in root_holes_sizes:
            root_holes_sizes[root_label] = 0

        root_holes_sizes[root_label] += hole_sizes[label]

    hole_distribution = {}

    # go through all elements in neighbor label dicts
    for root_label in root_holes_sizes.keys():
        hole_size = root_holes_sizes[root_label]

        if not hole_size in hole_distribution:
            hole_distribution[hole_size] = 1
        else:
            hole_distribution[hole_size] += 1



def EvaluateSkeletons(meta_filename):
    data = ReadMetaData(meta_filename)

    # make sure a results folder is specified
    assert (not data.EvaluationDirectory() == None)

    # read in statistics about this data set
    statistics_directory = '{}/statistics'.format(data.TempDirectory())
    statistics_filename = '{}/combined-statistics.pickle'.format(statistics_directory)
    statistics = ReadPickledData(statistics_filename)

    label_volumes = statistics['label_volumes']

    total_volume = 0
    total_thinned_skeleton_length = 0
    total_refined_skeleton_length = 0

    # get the output filename
    evaluation_directory = data.EvaluationDirectory()
    if not os.path.exists(evaluation_directory):
        os.makedirs(evaluation_directory, exist_ok=True)

    output_filename = '{}/skeleton-results.txt'.format(evaluation_directory)
    fd = open(output_filename, 'w')

    for label in sorted(label_volumes):
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
        print ('  Topological Thinning:   {:10d}    ({:05.2f}%)  {:10.2f}x'.format(thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
        print ('  Skeleton Refinement:    {:10d}    ({:05.2f}%)  {:10.2f}x'.format(refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
        print ('  Total:                                ({:05.2f}%)  {:10.2f}x'.format(total_skeleton_percent, total_skeleton_reduction))

        fd.write ('Label: {}\n'.format(label))
        fd.write ('  Input Volume:           {:10d}\n'.format(volume))
        fd.write ('  Topological Thinning:   {:10d}    ({:05.2f}%)  {:10.2f}x\n'.format(thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
        fd.write ('  Skeleton Refinement:    {:10d}    ({:05.2f}%)  {:10.2f}x\n'.format(refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
        fd.write ('  Total:                                ({:05.2f}%)  {:10.2f}x\n'.format(total_skeleton_percent, total_skeleton_reduction))

    # calculate the percent and reduction of total voxels remaining
    thinned_remaining_percent = 100 * total_thinned_skeleton_length / total_volume
    thinning_reduction_factor = total_volume / total_thinned_skeleton_length
    refined_remaining_percent = 100 * total_refined_skeleton_length / total_thinned_skeleton_length
    refinement_reduction_factor = total_thinned_skeleton_length / total_refined_skeleton_length

    # caluclate the total percent/reduction after all steps
    total_skeleton_percent = 100 * total_refined_skeleton_length / total_volume
    total_skeleton_reduction = total_volume / total_refined_skeleton_length

    print ('Input Volume:             {:10d}'.format(total_volume))
    print ('Topological Thinning:     {:10d}    ({:05.2f}%)  {:10.2f}x'.format(total_thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
    print ('Skeleton Refinement:      {:10d}    ({:05.2f}%)  {:10.2f}x'.format(total_refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
    print ('Total:                                  ({:05.2f}%)  {:10.2f}x'.format(total_skeleton_percent, total_skeleton_reduction))

    fd.write ('Input Volume:             {:10d}\n'.format(total_volume))
    fd.write ('Topological Thinning:     {:10d}    ({:05.2f}%)  {:10.2f}x\n'.format(total_thinned_skeleton_length, thinned_remaining_percent, thinning_reduction_factor))
    fd.write ('Skeleton Refinement:      {:10d}    ({:05.2f}%)  {:10.2f}x\n'.format(total_refined_skeleton_length, refined_remaining_percent, refinement_reduction_factor))
    fd.write ('Total:                                  ({:05.2f}%)  {:10.2f}x\n'.format(total_skeleton_percent, total_skeleton_reduction))

    # close the file
    fd.close()



def FindEndpoints(data, skeleton, somata_surface):
    # convert the skeleton to a set for faster access
    skeleton = set(skeleton)

    # find all endpoints in the skeleton (zero or one neighbor in the skeleton)
    endpoints = []

    # iterate over all skeleton points
    for pt in skeleton:
        iz, iy, ix = data.GlobalIndexToIndices(pt)

        # number of neighbors for this skeleton
        nneighbors = 0

        # consider the 26-connected neighborhood
        for iw in [iz - 1, iz, iz + 1]:
            for iv in [iy - 1, iy, iy + 1]:
                for iu in [ix - 1, ix, ix + 1]:
                    # skip when the same voxel
                    if iz == iw and iy == iv and ix == iu: continue

                    # get the linear index
                    neighbor_index = data.GlobalIndicesToIndex(iw, iv, iu)

                    if neighbor_index in skeleton or neighbor_index in somata_surface:
                        nneighbors += 1

        if nneighbors < 2:
            endpoints.append(pt)

    return endpoints



def EvaluateNeuralReconstructionIntegrity(meta_filename):
    data = ReadMetaData(meta_filename)

    synapses_per_label = {}

    # read in all of the synapses from all of the blocks
    synapse_directory = data.SynapseDirectory()
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                synapses_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pts'.format(synapse_directory, iz, iy, ix)

                # ignore the local coordinates
                block_synapses, _ = ReadPtsFile(data, synapses_filename)

                # add all synapses for each label in this block to the global synapses
                for label in block_synapses.keys():
                    if not label in synapses_per_label:
                        synapses_per_label[label] = []

                    synapses_per_label[label] += block_synapses[label]

    # for each label, find if synapses correspond to endpoints
    for label in range(1, data.NLabels()):
        # read the refined skeleton for this synapse
        skeleton_directory = '{}/skeletons'.format(data.SkeletonOutputDirectory())
        skeleton_filename = '{}/{:016d}.pts'.format(skeleton_directory, label)

        # skip over labels not processed
        if not os.path.exists(skeleton_filename): continue

        # get the synapses only for this one label
        synapses = synapses_per_label[label]

        # ignore the local coordinates
        skeletons, _ = ReadPtsFile(data, skeleton_filename)
        skeleton = skeletons[label]

        # read in the somata surfaces (points on the surface should not count as endpoints)
        somata_directory = '{}/somata_surfaces'.format(data.TempDirectory())
        somata_filename = '{}/{:016d}.pts'.format(somata_directory, label)

        # path may not exist if soma not found
        if os.path.exists(somata_filename):
            somata_surfaces, _ = ReadPtsFile(data, somata_filename)
            somata_surface = set(somata_surfaces[label])
        else:
            somata_surface = set()

        # get the endpoints in this skeleton for this label
        endpoints = FindEndpoints(data, skeleton, somata_surface)

        # TODO



def EvaluateWidths(data, label):
    # get the resolution of this data
    resolution = data.Resolution()

    # read the width attributes filename
    widths_directory = '{}/widths'.format(data.SkeletonOutputDirectory())
    width_filename = '{}/{:016d}.pts'.format(widths_directory, label)

    # skip over labels not processed
    if not os.path.exists(width_filename): return

    # read the width attributes
    widths, input_label = ReadAttributePtsFile(data, width_filename)
    assert (input_label == label)

    # get the surface filename
    surfaces_filename = '{}/{:016d}.pts'.format(data.SurfacesDirectory(), label)

    # read the surfaces, ignore local coordinates
    surfaces, _ = ReadPtsFile(data, surfaces_filename)
    surface = surfaces[label]
    npoints = len(surface)

    # conver the surface into a numpy point cloud
    np_point_cloud = np.zeros((npoints, 3), dtype=np.int32)
    for index, iv in enumerate(surface):
        # convert the index into indices
        iz, iy, ix = data.GlobalIndexToIndices(iv)

        # set the point cloud value according to the resolutions
        np_point_cloud[index,:] = (resolution[OR_Z] * iz, resolution[OR_Y] * iy, resolution[OR_X] * ix)

        index += 1

    # create empty dictionary for all results
    results = {}

    # keep track of all errors for this label
    results['errors'] = []
    results['estimates'] = 0
    results['ground_truths'] = 0

    # iterate over all skeleton points
    for iv in widths.keys():
        # get the estimated width at this location
        width = widths[iv]

        iz, iy, ix = data.GlobalIndexToIndices(iv)

        # convert the coordinates into a 2d vector with the resolutions
        vec = np.zeros((1, 3), dtype=np.int32)
        vec[0,:] = (resolution[OR_Z] * iz, resolution[OR_Y] * iy, resolution[OR_X] * ix)

        # get the min distance from this point to the surface (true width)
        min_distance = scipy.spatial.distance.cdist(np_point_cloud, vec).min()

        results['errors'].append(abs(width - min_distance))
        results['estimates'] += width
        results['ground_truths'] += min_distance

    # skip over vacuous skeletons
    if len(results['errors']) < 2: return

    # output the errors, estimates, and ground truths to a pickled file
    tmp_widths_directory = '{}/results/widths'.format(data.TempDirectory())
    if not os.path.exists(tmp_widths_directory):
        os.makedirs(tmp_widths_directory, exist_ok=True)

    output_filename = '{}/{:016d}.pickle'.format(tmp_widths_directory, label)
    PickleData(results, output_filename)



def CombineEvaluatedWidths(data):
    errors = []
    estimates = 0
    ground_truths = 0

    # get the output filename
    evaluation_directory = data.EvaluationDirectory()
    if not os.path.exists(evaluation_directory):
        os.makedirs(evaluation_directory, exist_ok=True)

    output_filename = '{}/widths-results.txt'.format(evaluation_directory)
    fd = open(output_filename, 'w')

    # for each label, read in the surface and the widths generated
    for label in range(1, data.NLabels()):
        # read the generated widths
        tmp_widths_directory = '{}/results/widths'.format(data.TempDirectory())
        widths_filename = '{}/{:016d}.pickle'.format(tmp_widths_directory, label)

        # skip over files that do not exist
        if not os.path.exists(widths_filename): continue

        results = ReadPickledData(widths_filename)

        # output the results and update the average error
        print ('Label: {}'.format(label))
        print ('  Mean Absolute Error: {:0.4f} (\u00B1{:0.2f}) nanometers'.format(statistics.mean(results['errors']), statistics.stdev(results['errors'])))
        print ('  Estimated Widths: {:0.4f}'.format(results['estimates']))
        print ('  Ground Truth Widths: {:0.4f}'.format(results['ground_truths']))
        print ('  Percent Different: {:0.2f}%'.format(100.0 * (results['estimates'] - results['ground_truths']) / results['ground_truths']))

        fd.write ('Label: {}\n'.format(label))
        fd.write ('  Mean Absolute Error: {:0.4f} (\u00B1{:0.2f}) nanometers\n'.format(statistics.mean(results['errors']), statistics.stdev(results['errors'])))
        fd.write ('  Estimated Widths: {:0.4f}\n'.format(results['estimates']))
        fd.write ('  Ground Truth Widths: {:0.2f}\n'.format(results['ground_truths']))
        fd.write ('  Percent Different: {:0.2f}%\n'.format(100.0 * (results['estimates'] - results['ground_truths']) / results['ground_truths']))

        # update global information
        errors += results['errors']
        estimates += results['estimates']
        ground_truths += results['ground_truths']

    print ('Total Volume')
    print ('  Mean Absolute Error: {:0.4f} (\u00B1{:0.2f}) nanometers'.format(statistics.mean(errors), statistics.stdev(errors)))
    print ('  Estimated Widths: {:0.4f}'.format(estimates))
    print ('  Ground Truth Widths: {:0.4f}'.format(ground_truths))
    print ('  Percent Different: {:0.2f}%'.format(100.0 * (estimates - ground_truths) / ground_truths))

    fd.write ('Total Volume\n')
    fd.write ('  Mean Absolute Error: {:0.4f} (\u00B1{:0.2f}) nanometers\n'.format(statistics.mean(errors), statistics.stdev(errors)))
    fd.write ('  Estimated Widths: {:0.4f}\n'.format(estimates))
    fd.write ('  Ground Truth Widths: {:0.4f}\n'.format(ground_truths))
    fd.write ('  Percent Different: {:0.2f}%\n'.format(100.0 * (estimates - ground_truths) / ground_truths))



def EvaluateWidthsSequentially(meta_filename):
    data = ReadMetaData(meta_filename)

    # iterate over all labels and generate width statistics
    for label in range(1, data.NLabels()):
        #EvaluateWidths(data, label)
        pass

    CombineEvaluatedWidths(data)
