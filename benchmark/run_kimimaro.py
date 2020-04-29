
# LISTING 1: Producing Skeletons from a labeled image.
import h5py
import kimimaro
from cloudvolume import PrecomputedSkeleton
import numpy as np
import os
import time

def ReadH5File(filename):
    with h5py.File(filename, 'r') as hf:
        data = np.array(hf[list(hf.keys())[0]])

    data = np.swapaxes(data,0,2)
    return data

def getSkeleton(labels):
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
      # extra_targets_before=[ (27,33,100), (44,45,46) ], # target points in voxels
      # extra_targets_after=[ (27,33,100), (44,45,46) ], # target points in voxels
      dust_threshold=1000, # skip connected components with fewer than this many voxels
      anisotropy=(18,18,20), # default True
      fix_branching=True, # default True
      fix_borders=True, # default True
      progress=True, # default False, show progress bar
      parallel=1, # <= 0 all cpu, 1 single process, 2+ multiprocess
      parallel_chunk_size=100, # how many skeletons to process before updating progress bar
    )

def writeSkeletonsToFile(skeletons, output_folder, bz, by, bx):
    for ID in skeletons.keys():
        fname = output_folder + "skel_out-label{:09d}-{:04d}z-{:04d}y-{:04d}x.swc".format(ID,bz,by,bx)
        with open(fname, 'w') as f:
            f.write(skeletons[ID].to_swc())

        print("Skeleton written to " + fname + " with "+ str(len(skeletons[ID].vertices))+ " vertices")

def writeFinalSkeletonToFile(skeleton, label, output_folder):
    fname = output_folder + "skel_out-final-label{:09d}.swc".format(label)
    with open(fname, 'w') as f:
        f.write(skeleton.to_swc())

def readSkelFromFile(fname, bz, by, bx, bsize, anisotropy):

    print("Reading from file: " + fname)

    with open(fname, 'r') as f:
        inp_swc = f.read()

    skel_read = PrecomputedSkeleton.from_swc(inp_swc)

    x_offset = bx*bsize[0]*anisotropy[0]
    y_offset = by*bsize[1]*anisotropy[1]
    z_offset = bz*bsize[2]*anisotropy[2]

    print("Block: " + str((bx,by,bz)))
    print("Offset: "+ str((x_offset,y_offset,z_offset)))

    skel_read.transform = np.array([[1,0,0,x_offset],
                                    [0,1,0,y_offset],
                                    [0,0,1,z_offset]])
    print("transform: " + str(skel_read.transform))

    # print("xmin, xmax: " + str(np.min(skel_read.vertices[:,0])) + ", " + str(np.max(skel_read.vertices[:,0])))
    # print("ymin, ymax: " + str(np.min(skel_read.vertices[:,1])) + ", " + str(np.max(skel_read.vertices[:,1])))
    # print("zmin, zmax: " + str(np.min(skel_read.vertices[:,2])) + ", " + str(np.max(skel_read.vertices[:,2])))
    # print("----------------------------")
    #
    skel_read.apply_transform()
    #
    # print("xmin, xmax: " + str(np.min(skel_read.vertices[:,0])) + ", " + str(np.max(skel_read.vertices[:,0])))
    # print("ymin, ymax: " + str(np.min(skel_read.vertices[:,1])) + ", " + str(np.max(skel_read.vertices[:,1])))
    # print("zmin, zmax: " + str(np.min(skel_read.vertices[:,2])) + ", " + str(np.max(skel_read.vertices[:,2])))

    skel_read.transform = np.array([[1,0,0,0],
                                    [0,1,0,0],
                                    [0,0,1,0]])


    return skel_read

def addIDs(all_ids, skels):
    for item in skels.keys():
        all_ids.add(item)
    print("All IDs so far: " + str(all_ids))

if __name__ == "__main__":

    input_folder = "/n/pfister_lab2/Lab/tfranzmeyer/exp/input/raw_segmentation/Zebrafinch/0512x0512x0512/"
    output_folder = "/n/pfister_lab2/Lab/tfranzmeyer/baseline_code/output_files/"

    bz_range = range(0,2)
    by_range = range(0,2)
    bx_range = range(0,2)

    bsize = (512,512,512)
    anisotropy=(18,18,20)

    all_ids = set()
    # all_ids = {25,28,29,39,40,41,49,55,64,65,72,79,81,95,103,107,116,118,127,134,135,136,146,149,154,157,166,169,182,183,184,185,187,189,191,194,196,198, 207, 212, 215, 227, 235, 237, 238, 244, 246}

    start_time_thinning = time.time()

    for bz in bz_range:
        for by in by_range:
            for bx in bx_range:

                fname = input_folder + "{:04d}z-{:04d}y-{:04d}x.h5".format(bz,by,bx)
                print("processing "+ fname)
                labels = ReadH5File(fname)
                skels_out = getSkeleton(labels)
                writeSkeletonsToFile(skels_out, output_folder, bz, by, bx)
                addIDs(all_ids, skels_out)

    total_time_thinning = time.time()-start_time_thinning
    print("total time thinning: " + str(total_time_thinning))

    start_time_combine = time.time()

    for label in all_ids:
        print("----------------------------------------------------")
        print("Combining skeletons for label " + str(label))
        all_skels = []

        for bz in bz_range:
            for by in by_range:
                for bx in bx_range:

                    fname = output_folder + "skel_out-label{:09d}-{:04d}z-{:04d}y-{:04d}x.swc".format(label,bz,by,bx)
                    if os.path.exists(fname):
                        skel_read = readSkelFromFile(fname, bz, by, bx, bsize, anisotropy)
                        print("Adding part from block " + str((bz,by,bx)) + " with " + str(len(skel_read.vertices)) + " vertices")
                        all_skels.insert(0, skel_read)

        skel_joined = kimimaro.join_close_components(all_skels, radius=1500) # 1500 units threshold
        print("Skeleton joined with " + str(len(skel_joined.vertices)) + " vertices")
        skel_final = kimimaro.postprocess(skel_joined, dust_threshold=1000, tick_threshold=3500)
        print("Skeleton final with " + str(len(skel_final.vertices)) + " vertices")
        writeFinalSkeletonToFile(skel_final, label, output_folder)

        try:
            print("xmin, xmax: " + str(np.min(skel_final.vertices[:,0])) + ", " + str(np.max(skel_final.vertices[:,0])))
            print("ymin, ymax: " + str(np.min(skel_final.vertices[:,1])) + ", " + str(np.max(skel_final.vertices[:,1])))
            print("zmin, zmax: " + str(np.min(skel_final.vertices[:,2])) + ", " + str(np.max(skel_final.vertices[:,2])))
        except:
            print("not able to print")

    print("total time combine: " + str(time.time()-start_time_combine))
    print("total time thinning: " + str(total_time_thinning))
