import os
import time



import numpy as np



from numba import jit, types



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPtsFile, WritePtsFile



@jit(nopython=True)
def ProduceSurfacesFromSegmentation(segmentation):
    zres, yres, xres = segmentation.shape

    # create a univeral list of surface voxels
    surfaces = []

    # create a set of all the labels in this block
    labels = set()

    # iterate over all voxels
    for iz in range(zres):
        for iy in range(yres):
            for ix in range(xres):
                label = segmentation[iz,iy,ix]

                # skip over background elements
                if not label: continue

                if not label in labels:
                    labels.add(label)

                # consider the six neighborhood
                surface = False
                if iz > 0 and not label == segmentation[iz-1,iy,ix]: surface = True
                if iy > 0 and not label == segmentation[iz,iy-1,ix]: surface = True
                if ix > 0 and not label == segmentation[iz,iy,ix-1]: surface = True
                if iz < zres - 1 and not label == segmentation[iz+1,iy,ix]: surface = True
                if iy < yres - 1 and not label == segmentation[iz,iy+1,ix]: surface = True
                if ix < xres - 1 and not label == segmentation[iz,iy,ix+1]: surface = True

                # add to the list of surfaces
                if surface: surfaces.append((iz, iy, ix))

    return surfaces, labels



def GenerateSurfacesPerBlock(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # read in the segmentation for this block
    read_time = time.time()
    segmentation = data.ReadSegmentationBlock(iz, iy, ix)
    read_time = time.time() - read_time

    surface_time = time.time()
    surfaces, labels = ProduceSurfacesFromSegmentation(segmentation)

    # create a dictionary of labels to surface lists
    surfaces_per_label = {}
    for label in labels:
        surfaces_per_label[label] = []

    # get the size of this block
    zres, yres, xres = segmentation.shape

    # update all surface lists
    for (ik, ij, ii) in surfaces:
        label = segmentation[ik, ij, ii]

        # convert to linear index
        voxel_index = ik * yres * xres + ij * yres + ii
        surfaces_per_label[label].append(voxel_index)

    surface_time = time.time() - surface_time

    # write the surfaces to
    write_time = time.time()

    # get the tmp filename
    tmp_directory = data.TempBlockDirectory(iz, iy, ix)
    surface_directory = '{}/surfaces'.format(tmp_directory)
    if not os.path.exists(surface_directory):
        os.makedirs(surface_directory, exist_ok = True)

    for label in sorted(surfaces_per_label.keys()):
        surface_filename = '{}/{:016d}.pts'.format(surface_directory, label)

        # write each points file independently
        WritePtsFile(data, surface_filename, {label: surfaces_per_label[label]}, (iz, iy, ix), input_local_indices = True)

    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Generated Surfaces Time: {:0.2f} seconds.'.format(surface_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))



def CombineSurfaceVoxels(data):
    # start timing statistics
    total_time = time.time()

    # create new directory for the surfaces
    tmp_directory = data.TempDirectory()
    surface_directory = '{}/surfaces'.format(tmp_directory)
    if not os.path.exists(surface_directory):
        os.makedirs(surface_directory, exist_ok = True)

    # iterate over all labels
    for label in range(1, data.NLabels()):
        global_indices = []

        # iterate over all blocks and read the points
        for iz in range(data.StartZ(), data.EndZ()):
            for iy in range(data.StartY(), data.EndY()):
                for ix in range(data.StartX(), data.EndX()):
                    tmp_block_directory = data.TempBlockDirectory(iz, iy, ix)

                    block_surface_filename = '{}/surfaces/{:016d}.pts'.format(tmp_block_directory, label)

                    # skip if this file does not exist (this label does not occur in this block)
                    if not os.path.exists(block_surface_filename): continue

                    global_block_indices, _ = ReadPtsFile(data, block_surface_filename)

                    global_indices += global_block_indices[label]

        if len(global_indices):
            surface_filename = '{}/{:016d}.pts'.format(surface_directory, label)
            WritePtsFile(data, surface_filename, { label: global_indices }, input_local_indices = False)

    total_time = time.time() - total_time

    print ('Combined Surfaces Files: {:0.2f} seconds.'.format(total_time))



def CollectSurfacesSequentially(prefix):
    # read in the data for this block
    data = ReadMetaData(prefix)

    # compute the first step to save the walls of each file
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                GenerateSurfacesPerBlock(data, iz, iy, ix)

    CombineSurfaceVoxels(data)
