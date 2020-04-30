import os
import time
import numpy as np


from blockbased_synapseaware.utilities.constants import *

import kimimaro
from cloudvolume import PrecomputedSkeleton

def readSkelFromFile(fname, iz, iy, ix, bsize, anisotropy):

    print("Reading from file: " + fname)

    with open(fname, 'r') as f:
        inp_swc = f.read()

    skel_read = PrecomputedSkeleton.from_swc(inp_swc)

    # revert order from x y z to z y x
    vertices_copy = skel_read.vertices.copy()
    skel_read.vertices[:,0] = vertices_copy[:,2]
    skel_read.vertices[:,2] = vertices_copy[:,0]

    x_offset = ix*bsize[OR_X]*anisotropy[OR_X]
    y_offset = iy*bsize[OR_Y]*anisotropy[OR_Y]
    z_offset = iz*bsize[OR_Z]*anisotropy[OR_Z]

    transform_ = np.array([ [1,0,0,0],
                            [0,1,0,0],
                            [0,0,1,0]])

    transform_[0,3] = z_offset
    transform_[1,3] = y_offset
    transform_[2,3] = x_offset

    skel_read.transform = transform_

    skel_read.apply_transform()

    skel_read.transform = np.array([[1,0,0,0],
                                    [0,1,0,0],
                                    [0,0,1,0]])

    return skel_read

def writeFinalSkeletonToFile(skeleton, label, output_folder):

    # revert order from z y x to x y z
    vertices_copy = skeleton.vertices.copy()
    skeleton.vertices[:,0] = vertices_copy[:,2]
    skeleton.vertices[:,2] = vertices_copy[:,0]

    fname = output_folder + "skel_out-final-label{:09d}.swc".format(label)
    with open(fname, 'w') as f:
        f.write(skeleton.to_swc())

    del skeleton

def ConnectSkeletons(data):

    for label in range(0,data.NLabels()):

        print("--------------------- \n processing label {}".format(label))

        # start timing statistics
        total_time = time.time()

        read_time = time.time()
        # list to store skeletons of different blocks
        all_skels = []
        # iterate over all blocks and read in skeletons for respective label
        for iz in range(data.StartZ(), data.EndZ()):
            for iy in range(data.StartY(), data.EndY()):
                for ix in range(data.StartX(), data.EndX()):

                    # get the location for the temporary directory
                    tmp_directory = data.TempBlockDirectory(iz, iy, ix)

                    fname = tmp_directory + "/skel_out-label{:09d}-{:04d}z-{:04d}y-{:04d}x.swc".format(label,iz,iy,ix)
                    if os.path.exists(fname):
                        skel_read = readSkelFromFile(fname, iz, iy, ix, data.BlockSize(), data.Resolution())
                        all_skels.insert(0, skel_read)
                        print("Adding part from block " + str((iz,iy,ix)) + " with " + str(len(skel_read.vertices)) + " vertices")

        read_time = time.time() - read_time

        # if label not present, skip
        if len(all_skels)==0: continue

        # join skeleton components to one skeleton
        join_time = time.time()
        skel_joined = kimimaro.join_close_components(all_skels, radius=1500) # 1500 units threshold
        join_time = time.time() - join_time

        # postprocess and connect skeleton parts
        postprocess_time = time.time()
        skel_final = kimimaro.postprocess(skel_joined, dust_threshold=1000, tick_threshold=3500)
        postprocess_time = time.time() - postprocess_time

        # check if it actually contains vertices
        if skel_final.vertices.shape[1]==0: continue

        # write final skeleton to file
        write_time = time.time()
        out_dir = data.SkeletonOutputDirectory()
        writeFinalSkeletonToFile(skel_final, label, out_dir)
        write_time = time.time() - write_time

        total_time = time.time() - total_time

        print ('Read Time: {:0.2f} seconds.'.format(read_time))
        print ('Join Time: {:0.2f} seconds.'.format(join_time))
        print ('Postprocess Time: {:0.2f} seconds.'.format(postprocess_time))
        print ('Write Time: {:0.2f} seconds.'.format(write_time))
        print ('Total Time: {:0.2f} seconds.'.format(total_time))

        # output timing statistics
        timing_directory = '{}/skeletons-combine'.format(data.TimingDirectory())
        if not os.path.exists(timing_directory):
            os.makedirs(timing_directory, exist_ok=True)
        timing_filename = '{}/{:016d}.txt'.format(timing_directory, label)
        with open(timing_filename, 'w') as fd:
            fd.write ('Read Time: {:0.2f} seconds.\n'.format(read_time))
            fd.write ('Join Time: {:0.2f} seconds.\n'.format(join_time))
            fd.write ('Postprocess Time: {:0.2f} seconds.\n'.format(postprocess_time))
            fd.write ('Write Time: {:0.2f} seconds.\n'.format(write_time))
            fd.write ('Total Time: {:0.2f} seconds.\n'.format(total_time))
