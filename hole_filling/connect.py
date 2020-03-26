import time



from numba import jit, types
from numba.typed import Dict



from blockbased_synapseaware.hole_filling.components import FindBackgroundComponentsAssociatedLabels, Set2Dictionary
from blockbased_synapseaware.utilities.dataIO import PickleData, PickleNumbaData, ReadH5File, ReadPickledData
from blockbased_synapseaware.utilities.constants import BORDER_CONTACT




# suppress deprecation warnings (future use will require typed.Set - not implemented)
from numba.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)



@jit(nopython=True)
def FindLabelsAdjacentToGlobalBorder(label_set, seg_wall):
    wall_shape = seg_wall.shape

    # go through all pixels along this wall
    for ij in range(wall_shape[0]):
        for ii in range(wall_shape[1]):
            label_set.add((seg_wall[ij,ii], BORDER_CONTACT))

    return label_set



def ConnectBlockToGlobalBorder(label_set, tmp_directory, axis, direction):
    # read in the wall for this border
    seg_wall_filename = '{}/{}-{}-hole-filling.h5'.format(tmp_directory, axis, direction)

    seg_wall = ReadH5File(seg_wall_filename)

    # all pixels along the wall connect to the boundary
    label_set = FindLabelsAdjacentToGlobalBorder(label_set, seg_wall)

    return label_set



@jit(nopython=True)
def FindLabelsBetweenAdjacentBlocks(label_set, current_seg_wall, neighbor_seg_wall):
    wall_shape = current_seg_wall.shape

    assert (current_seg_wall.shape == neighbor_seg_wall.shape)

    # go through all pixels along this wall
    for ij in range(wall_shape[0]):
        for ii in range(wall_shape[1]):
            label_set.add((current_seg_wall[ij,ii], neighbor_seg_wall[ij,ii]))
            label_set.add((neighbor_seg_wall[ij,ii], current_seg_wall[ij,ii]))

    return label_set



def ConnectBlocks(data, label_set, iz, iy, ix, axis):
    # get the (z, y, x) coordinates for the neighbor above this
    if axis == 'z':
        neighbor_iz = iz + 1
        neighbor_iy = iy
        neighbor_ix = ix
    if axis == 'y':
        neighbor_iz = iz
        neighbor_iy = iy + 1
        neighbor_ix = ix
    if axis == 'x':
        neighbor_iz = iz
        neighbor_iy = iy
        neighbor_ix = ix + 1

    # get the directory for current/neighbor
    tmp_current_directory = data.TempBlockDirectory(iz, iy, ix)
    tmp_neighbor_directory = data.TempBlockDirectory(neighbor_iz, neighbor_iy, neighbor_ix)

    # get the filenames for the current wall and its neighbor
    # the maximum of the current wall links to the min wall of its neighbor
    current_wall_filename = '{}/{}-max-hole-filling.h5'.format(tmp_current_directory, axis)
    neighbor_wall_filename = '{}/{}-min-hole-filling.h5'.format(tmp_neighbor_directory, axis)

    current_seg_wall = ReadH5File(current_wall_filename)
    neighbor_seg_wall = ReadH5File(neighbor_wall_filename)

    label_set = FindLabelsBetweenAdjacentBlocks(label_set, current_seg_wall, neighbor_seg_wall)

    return label_set



def ConnectLabelsAcrossBlocks(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # find all of the adjacent components across the boundaries
    adjacency_set_time = time.time()

    # create an empty list of adjacency sets
    neighbor_label_set_global = set()
    # add a fake tuple for numba to know fingerprint
    neighbor_label_set_global.add((BORDER_CONTACT, BORDER_CONTACT))

    # get the temporary directory for this dataset
    tmp_directory = data.TempBlockDirectory(iz, iy, ix)

    # this block occurs at the minimum in the z direction
    if iz == data.StartZ():
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'z', 'min')

    # this block occurs at the minimum of the y direction
    if iy == data.StartY():
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'y', 'min')

    # this block occurs at the minimum of the x direction
    if ix == data.StartX():
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'x', 'min')

    # this block occurs at the maximum in the z direction
    if iz == data.EndZ() - 1:
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'z', 'max')
    # this block has a neighbor in the positive z direction
    else:
        neighbor_label_set_global = ConnectBlocks(data, neighbor_label_set_global, iz, iy, ix, 'z')

    # this block occurs at the maximum of the y direction
    if iy == data.EndZ() - 1:
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'y', 'max')
    # this block has a neighbor in the positive y direction
    else:
        neighbor_label_set_global = ConnectBlocks(data, neighbor_label_set_global, iz, iy, ix, 'y')

    # this block occurs at the maximum of the x direction
    if ix == data.EndX() - 1:
        neighbor_label_set_global = ConnectBlockToGlobalBorder(neighbor_label_set_global, tmp_directory, 'x', 'max')
    # this block has a neighbor in the positive y direction
    else:
        neighbor_label_set_global = ConnectBlocks(data, neighbor_label_set_global, iz, iy, ix, 'x')

    # remove fake tuple from set
    neighbor_label_set_global.remove((BORDER_CONTACT, BORDER_CONTACT))

    adjacency_set_time = time.time() - adjacency_set_time

    # write the relevant files to disk
    write_time = time.time()
    PickleData(neighbor_label_set_global, '{}/neighbor-label-set-global.pickle'.format(tmp_directory))
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Adjacency Set Time: {:0.2f} seconds.'.format(adjacency_set_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))



def CombineAssociatedLabels(data):
    # start timing statistics
    total_time = time.time()

    # create empty sets/dicts
    neighbor_label_set_global = set()
    associated_label_dict_global = Dict.empty(key_type=types.int64, value_type=types.int64)
    undetermined_label_set_global = set()
    neighbor_label_dict_local = dict()

    read_time = time.time()

    # iterate over all blocks and read in global/local dicts
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                # get the location for the temporary directory
                tmp_directory = data.TempBlockDirectory(iz, iy, ix)

                # read the four sets/dicts for this one block
                block_neighbor_label_set_global = ReadPickledData('{}/neighbor-label-set-global.pickle'.format(tmp_directory))
                block_associated_label_dict = ReadPickledData('{}/associated-label-set-local.pickle'.format(tmp_directory))
                block_undetermined_label_set = ReadPickledData('{}/undetermined-label-set-local.pickle'.format(tmp_directory))
                block_neighbor_label_dict_local = ReadPickledData('{}/neighbor-label-dictionary-reduced.pickle'.format(tmp_directory))

                # combine the local datasets with the global ones
                neighbor_label_set_global = neighbor_label_set_global.union(block_neighbor_label_set_global)
                associated_label_dict_global.update(block_associated_label_dict)
                undetermined_label_set_global = undetermined_label_set_global.union(block_undetermined_label_set)
                neighbor_label_dict_local.update(block_neighbor_label_dict_local)

                # free memory
                del block_neighbor_label_set_global, block_associated_label_dict, block_undetermined_label_set, block_neighbor_label_dict_local


    read_time = time.time() - read_time

    background_associated_labels_time = time.time()

    # create a neighbor label dict building on the reduced labels read in for each block
    neighbor_label_dict_global = Set2Dictionary(neighbor_label_set_global, label_dict = neighbor_label_dict_local)
    # find groupings of negative neighbors surrounded by a single positive label
    associated_label_dict, undetermined_label_set, holes, non_holes = FindBackgroundComponentsAssociatedLabels(neighbor_label_dict_global, undetermined_label_set_global, associated_label_dict_global)

    # set all of the undetermined values to non_holes:
    for label in undetermined_label_set:
        associated_label_dict[label] = 0

    background_associated_labels_time = time.time() - background_associated_labels_time

    # write the associated labels to disk
    write_time = time.time()
    # write only one associated labels dictionary for all blocks
    tmp_directory = data.TempDirectory()
    PickleNumbaData(associated_label_dict, '{}/hole-filling-associated-labels.pickle'.format(tmp_directory))
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Background Components Associated Labels: {:0.2f} seconds.'.format(background_associated_labels_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
