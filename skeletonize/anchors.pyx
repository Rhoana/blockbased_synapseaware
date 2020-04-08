import os
import time
import ctypes



cimport cython
cimport numpy as np



import numpy as np



from blockbased_synapseaware.utilities.dataIO import ReadH5File, WriteH5File



cdef extern from 'cpp-skeletonize.h':
    void CppComputeAnchorPoints(const char *lookup_table_directory,
                                const char *tmp_current_directory,
                                const char *tmp_neighbor_directory,
                                long *current_seg,
                                long *neighbor_seg,
                                long input_volume_size[3],
                                long input_block_size[3],
                                long current_block_index[3],
                                char direction)



def SaveAnchorWalls(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # read in the original segmentation
    read_time = time.time()
    segmentation = data.ReadSegmentationBlock(iz, iy, ix)
    read_time = time.time() - read_time

    # write the walls for the segmentation to file
    write_time = time.time()

    # get the temp directory for this block
    tmp_directory = data.TempBlockDirectory(iz, iy, ix)

    WriteH5File(segmentation[0,:,:], '{}/z-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[-1,:,:], '{}/z-max-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,0,:], '{}/y-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,-1,:], '{}/y-max-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,:,0], '{}/x-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,:,-1], '{}/x-max-anchor-points.h5'.format(tmp_directory))
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    # print timing information
    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))

    # output timing statistics
    timing_directory = '{}/save-anchor-walls'.format(data.TimingDirectory())
    if not os.path.exists(timing_directory):
        os.makedirs(timing_directory, exist_ok=True)
    timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)
    with open(timing_filename, 'w') as fd:
        fd.write ('Read Time: {:0.2f} seconds.\n'.format(read_time))
        fd.write ('Write Time: {:0.2f} seconds.\n'.format(write_time))
        fd.write ('Total Time: {:0.2f} seconds.\n'.format(total_time))



def ComputeDirectionalAnchorPoints(data, iz, iy, ix, direction):
    # make sure the direction is recognized
    assert (direction == 'z' or direction == 'y' or direction == 'x')

    # don't calculate for the candidates on the edge
    if direction == 'z' and iz == data.EndZ() - 1: return
    if direction == 'y' and iy == data.EndY() - 1: return
    if direction == 'x' and ix == data.EndX() - 1: return

    # get the directory for current block
    tmp_current_directory = data.TempBlockDirectory(iz, iy, ix)

    # get directory for the neighbor block
    if direction == 'z': tmp_neighbor_directory = data.TempBlockDirectory(iz + 1, iy, ix)
    if direction == 'y': tmp_neighbor_directory = data.TempBlockDirectory(iz, iy + 1, ix)
    if direction == 'x': tmp_neighbor_directory = data.TempBlockDirectory(iz, iy, ix + 1)

    # get the filenames for the current and neighbor walls
    current_wall_filename = '{}/{}-max-anchor-points.h5'.format(tmp_current_directory, direction)
    neighbor_wall_filename = '{}/{}-min-anchor-points.h5'.format(tmp_neighbor_directory, direction)

    # read the current and neighbor wall
    current_seg_wall = ReadH5File(current_wall_filename)
    neighbor_seg_wall = ReadH5File(neighbor_wall_filename)

    # transform the numpy arrays into c++ arrays
    cdef np.ndarray[long, ndim=2, mode='c'] cpp_current_seg_wall = np.ascontiguousarray(current_seg_wall, dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=2, mode='c'] cpp_neighbor_seg_wall = np.ascontiguousarray(neighbor_seg_wall, dtype=ctypes.c_int64)

    # transform other variables
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_volume_size = np.ascontiguousarray(data.VolumeSize(), dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_block_size = np.ascontiguousarray(data.BlockSize(), dtype=ctypes.c_int64)

    lookup_table_directory = '{}/PGMImage'.format(os.path.dirname(__file__))

    # get the indices for both the current block
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_current_block_index = np.ascontiguousarray((iz, iy, ix), dtype=ctypes.c_int64)

    tmp_directory = data.TempDirectory()
    CppComputeAnchorPoints(lookup_table_directory.encode('utf-8'),
                           tmp_current_directory.encode('utf-8'),
                           tmp_neighbor_directory.encode('utf-8'),
                           &(cpp_current_seg_wall[0,0]),
                           &(cpp_neighbor_seg_wall[0,0]),
                           &(cpp_volume_size[0]),
                           &(cpp_block_size[0]),
                           &(cpp_current_block_index[0]),
                           ord(direction))



def ComputeAnchorPoints(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # compute the anchor points in the z direction
    z_anchor_computation_time = time.time()
    ComputeDirectionalAnchorPoints(data, iz, iy, ix, 'z')
    z_anchor_computation_time = time.time() - z_anchor_computation_time

    # compute the anchor points in the y direction
    y_anchor_computation_time = time.time()
    ComputeDirectionalAnchorPoints(data, iz, iy, ix, 'y')
    y_anchor_computation_time = time.time() - y_anchor_computation_time

    # compute the anchor points in the x direction
    x_anchor_computation_time = time.time()
    ComputeDirectionalAnchorPoints(data, iz, iy, ix, 'x')
    x_anchor_computation_time = time.time() - x_anchor_computation_time

    total_time = time.time() - total_time

    # print timing information
    print ('Z Anchor Computation Time: {:0.2f} seconds.'.format(z_anchor_computation_time))
    print ('Y Anchor Computation Time: {:0.2f} seconds.'.format(y_anchor_computation_time))
    print ('X Anchor Computation Time: {:0.2f} seconds.'.format(x_anchor_computation_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))

    # output timing statistics
    timing_directory = '{}/compute-anchor-points'.format(data.TimingDirectory())
    if not os.path.exists(timing_directory):
        os.makedirs(timing_directory, exist_ok=True)
    timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)
    with open(timing_filename, 'w') as fd:
        fd.write ('Z Anchor Computation Time: {:0.2f} seconds.\n'.format(z_anchor_computation_time))
        fd.write ('Y Anchor Computation Time: {:0.2f} seconds.\n'.format(y_anchor_computation_time))
        fd.write ('X Anchor Computation Time: {:0.2f} seconds.\n'.format(x_anchor_computation_time))
        fd.write ('Total Time: {:0.2f} seconds.\n'.format(total_time))
