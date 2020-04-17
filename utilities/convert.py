import os
import time



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPtsFile, WritePtsFile



def MapSynapsesAndSurfaces(input_meta_filename, output_meta_filename):
    # read in the meta data files
    input_data = ReadMetaData(input_meta_filename)
    output_data = ReadMetaData(output_meta_filename)

    input_synapse_directory = input_data.SynapseDirectory()
    output_synapse_directory = output_data.SynapseDirectory()

    # create the output synapse directory if it does not exist
    if not os.path.exists(output_synapse_directory):
        os.makedirs(output_synapse_directory, exist_ok = True)

    # read in all of the input syanpses
    input_synapses = {}

    for iz in range(input_data.StartZ(), input_data.EndZ()):
        for iy in range(input_data.StartY(), input_data.EndY()):
            for ix in range(input_data.StartX(), input_data.EndX()):
                input_synapse_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pts'.format(input_synapse_directory, iz, iy, ix)

                # ignore the local points
                global_pts, _ = ReadPtsFile(input_data, input_synapse_filename)

                for label in global_pts:
                    if not label in input_synapses:
                        input_synapses[label] = []

                    # add the array from this block to the input synapses
                    input_synapses[label] += global_pts[label]

    # create an output dictionary of synapses per block
    output_synapses_per_block = {}

    # iterate over all output blocks
    for iz in range(output_data.StartZ(), output_data.EndZ()):
        for iy in range(output_data.StartY(), output_data.EndY()):
            for ix in range(output_data.StartX(), output_data.EndX()):
                # create empty synapses_per_block dictionaries whose keys will be labels
                output_synapses_per_block[(iz, iy, ix)] = {}

    # for every label, go through the discovered synapses from the input data
    for label in input_synapses.keys():
        input_synapses_per_label = input_synapses[label]

        for input_global_index in input_synapses_per_label:
            # the global iz, iy, ix coordinates remain the same across blocks
            global_iz, global_iy, global_ix = input_data.GlobalIndexToIndices(input_global_index)

            # get the new block from the global coordinates
            output_block_iz = global_iz // output_data.BlockZLength()
            output_block_iy = global_iy // output_data.BlockYLength()
            output_block_ix = global_ix // output_data.BlockXLength()

            if not label in output_synapses_per_block[(output_block_iz, output_block_iy, output_block_ix)]:
                output_synapses_per_block[(output_block_iz, output_block_iy, output_block_ix)][label] = []

            # get the new global index
            output_global_index = output_data.GlobalIndicesToIndex(global_iz, global_iy, global_ix)

            output_synapses_per_block[(output_block_iz, output_block_iy, output_block_ix)][label].append(output_global_index)

    # write all of the synapse block files
    output_synapses_directory = output_data.SynapseDirectory()
    for iz in range(output_data.StartZ(), output_data.EndZ()):
        for iy in range(output_data.StartY(), output_data.EndY()):
            for ix in range(output_data.StartX(), output_data.EndX()):
                output_synapse_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pts'.format(output_synapse_directory, iz, iy, ix)

                # write the pts file (use global indices)
                WritePtsFile(output_data, output_synapse_filename, output_synapses_per_block[(iz, iy, ix)], input_local_indices = False)

    # get the input/output directories for the surfaces
    input_surfaces_directory = input_data.SurfacesDirectory()
    output_surfaces_directory = output_data.SurfacesDirectory()

    # create the output synapse directory if it does not exist
    if not os.path.exists(output_surfaces_directory):
        os.makedirs(output_surfaces_directory, exist_ok = True)

    # iterate over all labels
    for label in range(1, input_data.NLabels()):
        start_time = time.time()

        # skip over labels that do not exist
        input_surface_filename = '{}/{:016d}.pts'.format(input_surfaces_directory, label)
        if not os.path.exists(input_surface_filename): continue

        # read in the input global points
        input_global_points, _ = ReadPtsFile(input_data, input_surface_filename)

        # create an empty dictionary for the output points
        output_global_points = {}
        output_global_points[label] = []

        for input_global_index in input_global_points[label]:
            # the global iz, iy, ix coordinates remain the same across blocks
            global_iz, global_iy, global_ix = input_data.GlobalIndexToIndices(input_global_index)

            # get the new global index
            output_global_index = output_data.GlobalIndicesToIndex(global_iz, global_iy, global_ix)

            output_global_points[label].append(output_global_index)

        # write the new surface filename
        output_surface_filename = '{}/{:016d}.pts'.format(output_surfaces_directory, label)
        WritePtsFile(output_data, output_surface_filename, output_global_points, input_local_indices = False)

        print ('Completed label {} in {:0.2f} seconds'.format(label, time.time() - start_time))
