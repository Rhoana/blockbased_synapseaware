import os
import time
import ctypes



cimport cython
cimport numpy as np



import numpy as np



from blockbased_synapseaware.utilities.dataIO import ReadH5File



cdef extern from 'cpp-skeletonize.h':
    void CppTopologicalThinning(const char *lookup_table_directory,
                                const char *tmp_directory,
                                const char *synapse_directory,
                                long *segmentation,
                                long *somata,
                                float input_resolution[3],
                                long input_volume_size[3],
                                long input_block_size[3],
                                long current_block_index[3])



def TopologicalThinning(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # read in the segmentation block
    read_time = time.time()
    segmentation = data.ReadSegmentationBlock(iz, iy, ix)
    somata = data.ReadSomataBlock(iz, iy, ix)
    read_time = time.time() - read_time

    # thin each label in the block sequentially
    thinning_time = time.time()

    tmp_directory = data.TempBlockDirectory(iz, iy, ix)
    synapse_directory = data.SynapseDirectory()

    # make a temporary directory for the cell body surfaces, skeletons, and widths
    somata_surface_directory = '{}/somata_surfaces'.format(tmp_directory)
    if not os.path.exists(somata_surface_directory):
        os.mkdir(somata_surface_directory)
    skeletons_directory = '{}/skeletons'.format(tmp_directory)
    if not os.path.exists(skeletons_directory):
        os.mkdir(skeletons_directory)
    widths_directory = '{}/widths'.format(tmp_directory)
    if not os.path.exists(widths_directory):
        os.mkdir(widths_directory)

    # transform the segmentation and somata into a c++ array
    cdef np.ndarray[long, ndim=3, mode='c'] cpp_segmentation = np.ascontiguousarray(segmentation, dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=3, mode='c'] cpp_somata = np.ascontiguousarray(somata, dtype=ctypes.c_int64)

    # transform other variables
    cdef np.ndarray[float, ndim=1, mode='c'] cpp_resolution = np.ascontiguousarray(data.Resolution(), dtype=ctypes.c_float)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_volume_size = np.ascontiguousarray(data.VolumeSize(), dtype=ctypes.c_int64)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_block_size = np.ascontiguousarray(data.BlockSize(), dtype=ctypes.c_int64)

    # the lookup table is in the current directory
    lookup_table_directory = os.path.dirname(__file__)

    # get the current index for this block in c++ form
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_current_block_index = np.ascontiguousarray((iz, iy, ix), dtype=ctypes.c_int64)

    CppTopologicalThinning(lookup_table_directory.encode('utf-8'),
                           tmp_directory.encode('utf-8'),
                           synapse_directory.encode('utf-8'),
                           &(cpp_segmentation[0,0,0]),
                           &(cpp_somata[0,0,0]),
                           &(cpp_resolution[0]),
                           &(cpp_volume_size[0]),
                           &(cpp_block_size[0]),
                           &(cpp_current_block_index[0]))

    thinning_time = time.time() - thinning_time

    total_time =  time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Thinning Time: {:0.2f} seconds.'.format(thinning_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
