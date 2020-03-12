import time



from numba import jit



from blockbased_synapseaware.utilities.dataIO import PickleData, ReadH5File
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
    seg_wall_filename = '{}/{}-{}.h5'.format(tmp_directory, axis, direction)

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
    tmp_current_directory = data.TempComponentsDirectory(iz, iy, ix)
    tmp_neighbor_directory = data.TempComponentsDirectory(neighbor_iz, neighbor_iy, neighbor_ix)

    # get the filenames for the current wall and its neighbor
    # the maximum of the current wall links to the min wall of its neighbor
    current_wall_filename = '{}/{}-max.h5'.format(tmp_current_directory, axis)
    neighbor_wall_filename = '{}/{}-min.h5'.format(tmp_neighbor_directory, axis)

    current_seg_wall = ReadH5File(current_wall_filename)
    neighbor_seg_wall = ReadH5File(neighbor_wall_filename)

    label_set = FindLabelsBetweenAdjacentBlocks(label_set, current_seg_wall, neighbor_seg_wall)

    return label_set



def ConnectLabelsAcrossBlocks(data, iz, iy, ix):
    # start timing statistics
    start_time = time.time()

    # find all of the adjacent components across the boundaries
    adjacency_set_time = time.time()

    # create an empty list of adjacency sets
    neighbor_label_set_global = set()
    # add a fake tuple for numba to know fingerprint
    neighbor_label_set_global.add((BORDER_CONTACT, BORDER_CONTACT))

    # get the temporary directory for this dataset
    tmp_directory = data.TempComponentsDirectory(iz, iy, ix)

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

    total_time = time.time() - start_time

    print ('Adjacency Set Time: {:0.2f} seconds.'.format(adjacency_set_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
