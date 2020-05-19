
import os
import time



import numpy as np

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadPtsFile
import kimimaro
from cloudvolume import PrecomputedSkeleton
import blockbased_synapseaware.makeflow_example.makeflow_parameters as mf_param

def getSkeleton(labels, anisotropy_, targets_before_, targets_after_):
    return kimimaro.skeletonize(
      labels,
      teasar_params={
        'scale': 4,
        'const': 500, # physical units
        'pdrf_exponent': 4,
        'pdrf_scale': 100000,
        'soma_detection_threshold': 1100, # physical units
        'soma_acceptance_threshold': 3500, # physical units
        'soma_invalidation_scale': 1.0,
        'soma_invalidation_const': 300, # physical units
        'max_paths': 50, # default None
      },
      # object_ids=[ ... ], # process only the specified labels
      extra_targets_before=targets_before_, # target points in voxels
      extra_targets_after=targets_after_, # target points in voxels
      dust_threshold=1000, # skip connected components with fewer than this many voxels
      anisotropy=anisotropy_, # default True
      fix_branching=True, # default True
      fix_borders=True, # default True
      progress=True, # default False, show progress bar
      parallel=1, # <= 0 all cpu, 1 single process, 2+ multiprocess
      parallel_chunk_size=100, # how many skeletons to process before updating progress bar
    )

def writeSkeletonsToFile(skeletons, output_folder, iz, iy, ix):

    for ID in skeletons.keys():
        fname = output_folder + "/skel_out-label{:09d}-{:04d}z-{:04d}y-{:04d}x.swc".format(ID,iz,iy,ix)

        # revert order from z y x to x y z
        vertices_copy = skeletons[ID].vertices.copy()
        skeletons[ID].vertices[:,0] = vertices_copy[:,2]
        skeletons[ID].vertices[:,2] = vertices_copy[:,0]

        with open(fname, 'w') as f:
            f.write(skeletons[ID].to_swc())

        print("Skeleton written to " + fname + " with "+ str(len(skeletons[ID].vertices))+ " vertices")

    del skeletons

def ReadSynpasestoList(data, iz, iy, ix):

    # read in synapses for this block
    synapse_coordinates = []

    fname_synapses = '{}/{:04d}z-{:04d}y-{:04d}x.pts'.format(data.SynapseDirectory(), iz, iy, ix)
    _, synapse_local_indices = ReadPtsFile(data, fname_synapses)

    for ID in synapse_local_indices.keys():
        for index in synapse_local_indices[ID]:
            synapse_coordinates.insert(0, data.LocalIndexToIndices(index))

    print("inserted {} synapses".format(len(synapse_coordinates)))

    return synapse_coordinates


def ComputeSkeletonsPerBlock(data, iz, iy, ix):

    # start timing statistics
    total_time = time.time()

    # get the number of blocks in each dimension
    nblocks = data.NBlocks()
    block_volume = data.BlockVolume()

    # get the index for this block
    block_index = data.IndexFromIndices(iz, iy, ix)

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

    # save the components file to disk
    tmp_directory = data.TempBlockDirectory(iz, iy, ix)

    # create the folder if it does not exist
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory, exist_ok=True)

    # read in this volume
    read_time_synapses = time.time()
    # read in synapses for respective block and save coordinates in list which can be passed to skeletonize algorithm
    if mf_param.kimi_load_synapses:
        synapse_coordinates = ReadSynpasestoList(data, iz, iy, ix)
    else:
        synapse_coordinates = []
    read_time_synapses = time.time() - read_time_synapses

    # execute kimimaro skeletonize
    skeletonize_time = time.time()
    skels_out = getSkeleton(seg, data.Resolution(), [], synapse_coordinates)
    skeletonize_time = time.time() - skeletonize_time

    # write skeletons to files
    write_time = time.time()
    writeSkeletonsToFile(skels_out, tmp_directory, iz, iy, ix)
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Read Time Synapses: {:0.2f} seconds.'.format(read_time_synapses))
    print ('Skeletonize Time: {:0.2f} seconds.'.format(skeletonize_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))

    # output timing statistics
    timing_directory = '{}/skeletonize'.format(data.TimingDirectory())
    if not os.path.exists(timing_directory):
        os.makedirs(timing_directory, exist_ok=True)
    timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)
    with open(timing_filename, 'w') as fd:
        fd.write ('Read Time: {:0.2f} seconds.\n'.format(read_time))
        fd.write ('Read Time Synapses: {:0.2f} seconds.\n'.format(read_time_synapses))
        fd.write ('Skeletonize Time: {:0.2f} seconds.\n'.format(skeletonize_time))
        fd.write ('Write Time: {:0.2f} seconds.\n'.format(write_time))
        fd.write ('Total Time: {:0.2f} seconds.\n'.format(total_time))
