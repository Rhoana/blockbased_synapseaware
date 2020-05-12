import os
import math



import numpy as np
import scipy.spatial



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPtsFile, WritePtsFile
from blockbased_synapseaware.utilities.constants import *



def ConvertSynapsesAndProject(meta_filename, input_synapse_directory, xyz, conversion_rate):
    data = ReadMetaData(meta_filename)

    resolution = data.Resolution()

    # create an empty set of synapses
    synapses = {}

    # iterate over all labels
    for label in range(1, data.NLabels()):
        # read the surfaces for this label
        surface_filename = '{}/{:016d}.pts'.format(data.SurfacesDirectory(), label)
        # some surfaces (i.e., labels) will not exist in the volume
        if not os.path.exists(surface_filename): continue

        # read in the surface points, ignore the local coordinates
        surfaces, _ = ReadPtsFile(data, surface_filename)
        surface = surfaces[label]

        npts = len(surface)
        surface_point_cloud = np.zeros((npts, 3), dtype=np.int32)

        for index, iv in enumerate(surface):
            iz, iy, ix = data.GlobalIndexToIndices(iv)

            surface_point_cloud[index,:] = (iz * resolution[OR_Z], iy * resolution[OR_Y], ix * resolution[OR_X])

        # create an empty array for the synapses
        synapses[label] = []

        projected = 0
        missed = 0

        # read in the original synapses
        input_synapse_filename = '{}/syn_{:04}.txt'.format(input_synapse_directory, label)
        with open(input_synapse_filename, 'r') as fd:
            for line in fd:
                # separate the line into coordinates
                coordinates = line.strip().split()

                if xyz:
                    ix = round(int(coordinates[0]) / conversion_rate[OR_X])
                    iy = round(int(coordinates[1]) / conversion_rate[OR_Y])
                    iz = round(int(coordinates[2]) / conversion_rate[OR_Z])
                else:
                    iz = round(int(coordinates[0]) / conversion_rate[OR_Z])
                    iy = round(int(coordinates[1]) / conversion_rate[OR_Y])
                    ix = round(int(coordinates[2]) / conversion_rate[OR_X])

                # create a 2D vector for this point
                vec = np.zeros((1, 3), dtype=np.int32)
                vec[0,:] = (iz * resolution[OR_Z], iy * resolution[OR_Y], ix * resolution[OR_X])

                closest_point = surface[scipy.spatial.distance.cdist(surface_point_cloud, vec).argmin()]

                closest_iz, closest_iy, closest_ix = data.GlobalIndexToIndices(closest_point)

                deltaz = resolution[OR_Z] * (iz - closest_iz)
                deltay = resolution[OR_Y] * (iy - closest_iy)
                deltax = resolution[OR_X] * (ix - closest_ix)

                distance = math.sqrt(deltaz * deltaz + deltay * deltay + deltax * deltax)

                # skip distances that are clearly off (over 200 nanometers)
                max_deviation = 800
                if distance < max_deviation:
                    # add to the list of valid synapses
                    synapses[label].append(closest_point)
                    projected += 1
                else:
                    missed += 1

            print ('Projected: {}'.format(projected))
            print ('Missed: {}'.format(missed))

    # divide all synapses into blocks
    synapses_per_block = {}

    # iterate over all blocks
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                # create empty synapses_per_block dictionaries whose keys will be labels
                synapses_per_block[(iz, iy, ix)] = {}

    # for every label, iterate over the discovered synapses
    for label in synapses.keys():
        synapses_per_label = synapses[label]

        # iterate over all of the projected synapses
        for global_index in synapses_per_label:
            global_iz, global_iy, global_ix = data.GlobalIndexToIndices(global_index)

            block_iz = global_iz // data.BlockZLength()
            block_iy = global_iy // data.BlockYLength()
            block_ix = global_ix // data.BlockXLength()

            # create the array for this label per block if it does not exist
            if not label in synapses_per_block[(block_iz, block_iy, block_ix)]:
                synapses_per_block[(block_iz, block_iy, block_ix)][label] = []

            synapses_per_block[(block_iz, block_iy, block_ix)][label].append(global_index)

    # write all of the synapse block files
    synapse_directory = data.SynapseDirectory()
    if not os.path.exists(synapse_directory):
        os.makedirs(synapse_directory, exist_ok=True)

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                synapse_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pts'.format(synapse_directory, iz, iy, ix)

                # write the pts file (use global indices)
                WritePtsFile(data, synapse_filename, synapses_per_block[(iz, iy, ix)], input_local_indices = False)
