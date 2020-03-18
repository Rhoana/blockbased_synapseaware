import os
import time



import numpy as np



from numba import jit, types
from numba.typed import Dict



from blockbased_synapseaware.hole_filling.connected_components.cc3d import connected_components
from blockbased_synapseaware.utilities.dataIO import PickleData, PickleNumbaData, WriteH5File
from blockbased_synapseaware.utilities.constants import *



def ComputeConnected6Components(seg, background_start_label):
    # run connected components with 6 connectivity
    components = connected_components(seg, connectivity=6)

    # how many negative components are there
    n_background_components = -1 * np.min(components)

    # update the background_start_labels to be universally unique
    if background_start_label != -1:
        components[components < 0] = components[components < 0] + background_start_label

    return components, n_background_components



@jit(nopython=True)
def FindAdjacentLabelSetLocal(components):
    neighbor_label_set = set()

    zres, yres, xres = components.shape

    # consider all neighboring pairs within the volume
    for iz in range(0, zres - 1):
        for iy in range(0, yres - 1):
            for ix in range(0, xres - 1):

                # get the component at this location
                component = components[iz,iy,ix]

                # does this component differ from its neighbor in z
                if component != components[iz+1,iy,ix]:
                    neighbor_label_set.add((component, components[iz+1,iy,ix]))
                    neighbor_label_set.add((components[iz+1,iy,ix], component))

                # does this component differ from its neighbor in y
                if component != components[iz,iy+1,ix]:
                    neighbor_label_set.add((component, components[iz,iy+1,ix]))
                    neighbor_label_set.add((components[iz,iy+1,ix], component))

                # does this component differ from its neighbor in x
                if component != components[iz,iy,ix+1]:
                    neighbor_label_set.add((component, components[iz,iy,ix+1]))
                    neighbor_label_set.add((components[iz,iy,ix+1], component))

    # consider components on the first and last z slice
    for iz in [0, zres - 1]:
        for iy in range(0, yres):
            for ix in range(0, xres):

                #interconnect in plane
                component = components[iz,iy,ix]

                if iy < yres - 1:
                    if component != components[iz,iy+1,ix]:
                        neighbor_label_set.add((component, components[iz,iy+1,ix]))
                        neighbor_label_set.add((components[iz,iy+1,ix], component))

                if ix < xres - 1:
                    if component != components[iz,iy,ix+1]:
                        neighbor_label_set.add((component, components[iz,iy,ix+1]))
                        neighbor_label_set.add((components[iz,iy,ix+1], component))

                # write dict of border components paired with sufficiently high fake label
                neighbor_label_set.add((component, BORDER_CONTACT))

    # consider components on the first and last y slice
    for iy in [0, yres - 1]:
        for iz in range(0, zres):
            for ix in range(0, xres):

                #interconnect in plane
                component = components[iz,iy,ix]

                if iz < zres - 1:
                    if component != components[iz+1,iy,ix]:
                        neighbor_label_set.add((component, components[iz+1,iy,ix]))
                        neighbor_label_set.add((components[iz+1,iy,ix], component))

                if ix < xres - 1:
                    if component != components[iz,iy,ix+1]:
                        neighbor_label_set.add((component, components[iz,iy,ix+1]))
                        neighbor_label_set.add((components[iz,iy,ix+1], component))

                # write dict of border components paired with sufficiently high fake label
                neighbor_label_set.add((component, BORDER_CONTACT))

    # consider components on the first and last x slice
    for ix in [0, xres - 1]:
        for iz in range(0, zres):
            for iy in range(0, yres):

                #interconnect in plane
                component = components[iz,iy,ix]

                if iz < zres - 1:
                    if component != components[iz+1,iy,ix]:
                        neighbor_label_set.add((component, components[iz+1,iy,ix]))
                        neighbor_label_set.add((components[iz+1,iy,ix], component))

                if iy < yres - 1:
                    if component != components[iz,iy+1,ix]:
                        neighbor_label_set.add((component, components[iz,iy+1,ix]))
                        neighbor_label_set.add((components[iz,iy+1,ix], component))

                # write dict of border components paired with sufficiently high fake label
                neighbor_label_set.add((component, BORDER_CONTACT))

    return neighbor_label_set



def Set2Dictionary(label_set, label_dict = None):
    if label_dict == None:
        label_dict = dict()

    # go through all of the labels in the set
    for (label_one, label_two) in label_set:
        # background components can be neighbors if they cross a border

        # skip non-background components
        if label_one > 0: continue

        # create a dictionary entry for this label if it doesn't exist yet
        if not label_one in label_dict:
            label_dict[label_one] = [label_two]
        # otherwise append the label to the dictionary entry for label_one
        elif not label_two in label_dict[label_one]:
            label_dict[label_one].append(label_two)
        # when label_dict is not None, the element could already appear in the set

    return label_dict



def FindBackgroundComponentsAssociatedLabels(neighbor_label_dict, undetermined_label_set, associated_label_dict):
    # find which background components have only one non-background neighbor
    border_contact = set()
    holes = set()
    non_holes = set()

    #label = -7516291072

    # continue until there are no more undetermined components in the set
    while len(undetermined_label_set):
        query_component = undetermined_label_set.pop()

        # check to see if there is one neighbor which is a neuron
        if len(neighbor_label_dict[query_component]) == 1 and neighbor_label_dict[query_component][0] != BORDER_CONTACT:
            # there should never be a case where there is one background component neighbor
            assert (neighbor_label_dict[query_component][0] > 0)

            associated_label_dict[query_component] = neighbor_label_dict[query_component][0]
            holes.add(query_component)

        # otherwise, unroll all other neighbors to identify if hole or not
        else:
            # list of nodes to expand (initially just the neighbors of the background component)
            labels_to_expand = list(filter(lambda a : a < 0, neighbor_label_dict[query_component]))

            # iteratively expand labels
            while len(labels_to_expand):
                label = labels_to_expand.pop()

                if label == BORDER_CONTACT:
                    # add the border contact to the neighbor list
                    if not BORDER_CONTACT in neighbor_label_dict[query_component]:
                        neighbor_label_dict[query_component].append(BORDER_CONTACT)
                else:
                    for child in neighbor_label_dict[label]:
                        if not child in neighbor_label_dict[query_component] and not child == query_component:
                            neighbor_label_dict[query_component].append(child)
                            # if this component is also background, add to list of expandable nodes
                            if child < 0: labels_to_expand.append(child)

            # if there is contact with the border, add to border contact list
            if BORDER_CONTACT in neighbor_label_dict[query_component]:
                border_contact.add(query_component)
                for label in neighbor_label_dict[query_component]:
                    # all connected background components also connect to the border
                    if label < 0:
                        border_contact.add(label)
                        undetermined_label_set.remove(label)

            # if component lacks border contact, it can be determined as whole or not
            else:
                neuron_neighbors = list(filter(lambda a : a > 0, neighbor_label_dict[query_component]))
                # if there is only one neighbor it is a hole
                if len(neuron_neighbors) == 1:
                    associated_label_dict[query_component] = neuron_neighbors[0]
                    holes.add(query_component)
                    # all other background components adjacent to this neuron are also holes
                    for label in neighbor_label_dict[query_component]:
                        if label < 0:
                            # make sure the label agrees if already discovered
                            associated_label_dict[label] = neuron_neighbors[0]
                            undetermined_label_set.remove(label)
                            holes.add(label)
                # if there are more than one neighbor it is not a hole
                else:
                    associated_label_dict[query_component] = 0
                    non_holes.add(query_component)
                    for label in neighbor_label_dict[query_component]:
                        if label < 0:
                            # make sure the label agrees if already discovered
                            associated_label_dict[label] = 0
                            undetermined_label_set.remove(label)
                            non_holes.add(label)

    assert (not len(undetermined_label_set))

    # update the undetermined_label_set to equal the border_contact_set
    return associated_label_dict, border_contact, holes, non_holes



def PruneNeighborLabelSet(neighbor_label_set, holes, non_holes):
    neighbor_label_set_reduced = set()

    for (label_one, label_two) in neighbor_label_set:
        # do not include any elements already labeled or connected to the border
        if label_one in holes or label_one in non_holes: continue
        if label_two in holes or label_two in non_holes: continue
        if label_one == BORDER_CONTACT or label_two == BORDER_CONTACT: continue

        neighbor_label_set_reduced.add((label_one, label_two))

    return neighbor_label_set_reduced



def FindPerBlockConnectedComponents(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # get the number of blocks in each dimension
    nblocks = data.NBlocks()
    block_volume = data.BlockVolume()

    # get the index for this block
    block_index = data.IndexFromIndices(iz, iy, ix)

    # get the index for the background volumes
    background_start_label = -1 * block_index * block_volume

    # read in this volume
    read_time = time.time()
    seg = data.ReadRawSegmentationBlock(iz, iy, ix)
    read_time = time.time() - read_time

    # make sure the block is not larger than mentioned in param file
    assert (seg.shape[OR_Z] <= data.BlockZLength())
    assert (seg.shape[OR_Y] <= data.BlockYLength())
    assert (seg.shape[OR_X] <= data.BlockXLength())

    # pad the block with zeroes at the ends
    if seg.shape[OR_Z] < data.BlockZLength() or seg.shape[OR_Y] < data.BlockYLength() or seg.shape[OR_X] < data.BlockXLength():
        # make sure that the block is on one of the far edges
        assert (iz == data.EndZ() - 1 or iy == data.EndY() - 1 or ix == data.EndX() - 1)

        zpadding = data.ZBlockLength() - seg.shape[OR_Z]
        ypadding = data.YBlockLength() - seg.shape[OR_Y]
        xpadding = data.XBlockLength() - seg.shape[OR_X]

        # padding only goes at the far edges of the block
        seg = np.pad(seg, ((0, zpadding), (0, ypadding), (0, xpadding)), 'constant', constant_values = 0)

        # make sure the block is not smaller than mentioned in param file
        assert (seg.shape[OR_Z] == data.BlockZLength())
        assert (seg.shape[OR_Y] == data.BlockYLength())
        assert (seg.shape[OR_X] == data.BlockXLength())

    # call connected components algorithm for this block
    components_time = time.time()
    components, n_background_components = ComputeConnected6Components(seg, background_start_label)

    # delete original segmentation
    del seg

    # save the components file to disk
    tmp_directory = data.TempComponentsDirectory(iz, iy, ix)

    # create the folder if it does not exist
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory, exist_ok=True)

    # write the components and all walls to file
    WriteH5File(components, '{}/components.h5'.format(tmp_directory))
    WriteH5File(components[0,:,:], '{}/z-min-hole-filling.h5'.format(tmp_directory))
    WriteH5File(components[-1,:,:], '{}/z-max-hole-filling.h5'.format(tmp_directory))
    WriteH5File(components[:,0,:], '{}/y-min-hole-filling.h5'.format(tmp_directory))
    WriteH5File(components[:,-1,:], '{}/y-max-hole-filling.h5'.format(tmp_directory))
    WriteH5File(components[:,:,0], '{}/x-min-hole-filling.h5'.format(tmp_directory))
    WriteH5File(components[:,:,-1], '{}/x-max-hole-filling.h5'.format(tmp_directory))

    components_time = time.time() - components_time

    # find the set of adjacent labels, both inside the volume and the ones connected at the local border
    adjacency_set_time = time.time()
    neighbor_label_set = FindAdjacentLabelSetLocal(components)
    adjacency_set_time = time.time() - adjacency_set_time

    # delete the components (no longer needed)
    del components

    # create a dictionary of labels from the set
    background_associated_labels_time = time.time()
    neighbor_label_dict = Set2Dictionary(neighbor_label_set)

    # to start, none of the background components are determined
    undetermined_label_set = set(neighbor_label_dict.keys())
    # dictionary associated background components to labels
    associated_label_dict = Dict.empty(key_type=types.int64, value_type=types.int64)
    associated_label_dict, undetermined_label_set, holes, non_holes = FindBackgroundComponentsAssociatedLabels(neighbor_label_dict, undetermined_label_set, associated_label_dict)
    background_associated_labels_time = time.time() - background_associated_labels_time

    # remove from the neighbor label set border elements and those already determined as holes and non holes
    neighbor_label_set_reduced = PruneNeighborLabelSet(neighbor_label_set, holes, non_holes)
    neighbor_label_dict_reduced = Set2Dictionary(neighbor_label_set_reduced)

    # delete the temporary generated set and dictionary
    del neighbor_label_set, neighbor_label_dict

    # write the relevant files to disk
    write_time = time.time()
    PickleNumbaData(associated_label_dict, '{}/associated-label-set-local.pickle'.format(tmp_directory))
    PickleData(undetermined_label_set, '{}/undetermined-label-set-local.pickle'.format(tmp_directory))
    PickleData(neighbor_label_dict_reduced, '{}/neighbor-label-dictionary-reduced.pickle'.format(tmp_directory))
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Components Time: {:0.2f} seconds.'.format(components_time))
    print ('Adjacency Set Time: {:0.2f} seconds.'.format(adjacency_set_time))
    print ('Background Components Associated Labels: {:0.2f} seconds.'.format(background_associated_labels_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
