import os
import time
import ctypes



cimport cython
cimport numpy as np



import numpy as np



from blockbased_synapseaware.utilities.dataIO import ReadAttributePtsFile, WriteAttributePtsFile



cdef extern from 'cpp-skeletonize.h':
    void CppSkeletonRefinement(const char *tmp_directory,
                               const char *synapse_directory,
                               const char *skeleton_output_directory,
                               long label,
                               float input_resolution[3],
                               long input_volume_size[3],
                               long input_block_size[3],
                               long start_indices[3],
                               long nblocks[3])



def RefineSkeleton(data, label):
    # start timing statistics
    total_time = time.time()

    # keep track of refinement time
    refinement_time = time.time()

    # get directory structure
    tmp_directory = data.TempDirectory()
    synapse_directory = data.SynapseDirectory()

    # make sure the skeleton output directory exists
    skeleton_output_directory = data.SkeletonOutputDirectory()
    if not os.path.exists(skeleton_output_directory):
        os.makedirs(skeleton_output_directory, exist_ok = True)

    # create tmp directories for somata surfaces, synapses, and skeletons
    tmp_somata_surface_directory = '{}/somata_surfaces'.format(tmp_directory)
    if not os.path.exists(tmp_somata_surface_directory):
        os.makedirs(tmp_somata_surface_directory, exist_ok = True)
    tmp_synapse_surface_directory = '{}/synapses'.format(tmp_directory)
    if not os.path.exists(tmp_synapse_surface_directory):
        os.makedirs(tmp_synapse_surface_directory, exist_ok = True)
    tmp_skeletons_directory = '{}/skeletons'.format(tmp_directory)
    if not os.path.exists(tmp_skeletons_directory):
        os.makedirs(tmp_skeletons_directory, exist_ok = True)

    # create final output directories for skeletons, distances, and widths
    skeletons_directory = '{}/skeletons'.format(skeleton_output_directory)
    if not os.path.exists(skeletons_directory):
        os.makedirs(skeletons_directory, exist_ok = True)
    distances_directory = '{}/distances'.format(skeleton_output_directory)
    if not os.path.exists(distances_directory):
        os.makedirs(distances_directory, exist_ok = True)
    widths_directory = '{}/widths'.format(skeleton_output_directory)
    if not os.path.exists(widths_directory):
        os.makedirs(widths_directory, exist_ok = True)

    # transform other variables
    cdef np.ndarray[float, ndim=1, mode='c'] cpp_resolution = np.ascontiguousarray(data.Resolution(), dtype=ctypes.c_float)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_volume_size = np.ascontiguousarray(data.VolumeSize(), dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_block_size = np.ascontiguousarray(data.BlockSize(), dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_start_indices = np.ascontiguousarray(data.StartIndices(), dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_nblocks = np.ascontiguousarray(data.NBlocks(), dtype=ctypes.c_int64)

    CppSkeletonRefinement(tmp_directory.encode('utf-8'),
                          synapse_directory.encode('utf-8'),
                          skeleton_output_directory.encode('utf-8'),
                          label,
                          &(cpp_resolution[0]),
                          &(cpp_volume_size[0]),
                          &(cpp_block_size[0]),
                          &(cpp_start_indices[0]),
                          &(cpp_nblocks[0]))

    refinement_time = time.time() - refinement_time

    # update the widths to only have attributes corresponding to the refined skeleton
    widths_time = time.time()

    # first read in the distances file which has the final values for all the global indices
    distance_filename = '{}/distances/{:016d}.pts'.format(skeleton_output_directory, label)
    # skip over files that don't exist (labels that do not occur, e.g.)
    if not os.path.exists(distance_filename): return
    distances, input_label = ReadAttributePtsFile(data, distance_filename)
    assert (input_label == label)
    widths = {}

    # read in the widths in each block
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                # read the widths for this block if they exist
                tmp_block_directory = data.TempBlockDirectory(iz, iy, ix)
                widths_filename = '{}/widths/{:016d}.pts'.format(tmp_block_directory, label)
                if not os.path.exists(widths_filename): continue

                block_widths, input_label = ReadAttributePtsFile(data, widths_filename)
                assert (input_label == label)

                # if this voxel belongs to the refined skeleton, keep the width
                for (voxel_index, width) in block_widths.items():
                    if voxel_index in distances:
                        widths[voxel_index] = width

    assert (len(widths.keys()) == len(distances.keys()))

    output_widths_filename = '{}/widths/{:016d}.pts'.format(skeleton_output_directory, label)
    WriteAttributePtsFile(data, output_widths_filename, label, widths)

    widths_time = time.time() - widths_time

    total_time = time.time() - total_time

    print ('Refinement Time: {:0.2f} seconds.'.format(refinement_time))
    print ('Update Widths Time: {:0.2f} seconds.'.format(widths_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))

    # output timing statistics
    timing_directory = '{}/skeleton-refinement'.format(data.TimingDirectory())
    if not os.path.exists(timing_directory):
        os.makedirs(timing_directory, exist_ok=True)
    timing_filename = '{}/{:016d}.txt'.format(timing_directory, label)
    with open(timing_filename, 'w') as fd:
        fd.write ('Refinement Time: {:0.2f} seconds.\n'.format(refinement_time))
        fd.write ('Update Widths Time: {:0.2f} seconds.\n'.format(widths_time))
        fd.write ('Total Time: {:0.2f} seconds.\n'.format(total_time))
