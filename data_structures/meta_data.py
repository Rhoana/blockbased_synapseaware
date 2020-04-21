import os
import sys
import math
import h5py


import numpy as np



from blockbased_synapseaware.utilities.constants import *



class MetaData:

    def __init__(self, meta_filename):
        self.meta_filename = meta_filename
        # create default variable values
        self.raw_segmentation_path = None
        self.tmp_directory = None
        self.block_sizes = None
        self.volume_sizes = None
        self.max_label = -1
        # default start index value for the block
        self.start_indices = (0, 0, 0)
        # default values for number of blocks is -1, will be updated later
        self.nzblocks = -1
        self.nyblocks = -1
        self.nxblocks = -1
        # place to save the hole filled segmentations
        self.hole_filling_output_directory = None
        self.synapse_path = None
        self.somata_path = None
        self.surfaces_path = None
        # place to save the generated skeletons
        self.skeleton_output_directory = None
        self.figures_directory = None
        self.figure_description = None
        self.evaluation_directory = None
        self.resolution = None
        self.somata_downsample_rate = 0

        # open the meta file and read in requisite information

        with open(meta_filename, 'r') as fd:
            lines = [line for line in fd.readlines() if line.strip()]

            # meta files have pairs of lines with comments and values
            for iv in range(0, len(lines), 2):
                comment = lines[iv].strip()
                value = lines[iv + 1].strip()

                ##################
                ### INPUT DATA ###
                ##################

                if comment == '# path to raw segmentations':
                    self.raw_segmentation_path = value
                elif comment == '# path to synapses':
                    self.synapse_path = value
                elif comment == '# path to somata':
                    self.somata_path = value
                elif comment == '# path to surfaces':
                    self.surfaces_path = value

                ##########################
                ### DATA SPECIFICATION ###
                ##########################

                elif comment == '# block size (x, y, z)':
                    block_sizes = value.split('x')
                    # use order 2, 1, 0 to convert from xyz to zyx
                    self.block_sizes = (int(block_sizes[2]), int(block_sizes[1]), int(block_sizes[0]))
                elif comment == '# volume size (x, y, z)':
                    volume_sizes = value.split('x')
                    # use order 2, 1, 0 to convert from xyz to zyx
                    self.volume_sizes = (int(volume_sizes[2]), int(volume_sizes[1]), int(volume_sizes[0]))
                elif comment == '# start block indices (x, y, z)':
                    start_indices = value.split(',')
                    # use order 2, 1, 0 to convert from xyz to zyx
                    self.start_indices = (int(start_indices[2]), int(start_indices[1]), int(start_indices[0]))
                elif comment == '# number of blocks to skeletonize (x, y, z)':
                    nblocks = value.split('x')
                    # use order 2, 1, 0 to convert from xyz to zyx
                    self.nzblocks = int(nblocks[2])
                    self.nyblocks = int(nblocks[1])
                    self.nxblocks = int(nblocks[0])
                elif comment == '# resolution in nm (x, y, z)':
                    resolutions = value.split('x')
                    # use order 2, 1, 0 to convert from xyz to zyx
                    self.resolution = (float(resolutions[2]), float(resolutions[1]), float(resolutions[0]))
                elif comment == '# max label':
                    self.max_label = int(value)
                elif comment == '# somata downsample rate':
                    self.somata_downsample_rate = int(value)

                ##########################
                ### OUTPUT DIRECTORIES ###
                ##########################

                elif comment == '# temporary files directory':
                    self.tmp_directory = value
                elif comment == '# hole filling output directory':
                    self.hole_filling_output_directory = value

                elif comment == '# skeleton output directory':
                    self.skeleton_output_directory = value
                elif comment == '# evaluation directory':
                    self.evaluation_directory = value
                elif comment == '# figures directory':
                    self.figures_directory = value
                elif comment == '# figure title description':
                    self.figure_description = value
                else:
                    sys.stderr.write('Unrecognized meta file attribute: {}\n'.format(comment))
                    exit(-1)

        # make sure important values are initialized
        assert (not self.raw_segmentation_path == None)
        assert (not self.tmp_directory == None)
        assert (not self.max_label == -1)
        assert (not self.block_sizes == None)
        assert (not self.volume_sizes == None)
        assert (not self.synapse_path == None)
        assert (not self.resolution == None)

        # if a somata path is provided, downsample rate must be specified
        if not self.somata_path == None:
            assert (self.somata_downsample_rate)
        if self.somata_downsample_rate:
            assert (not self.somata_path == None)

        # if there will be figures, make sure there is a description
        if not self.figures_directory == None:
            assert (not self.figure_description == None)

        # create the tmp directory if it does not exist
        if not os.path.exists(self.tmp_directory):
            os.makedirs(self.tmp_directory, exist_ok=True)

        # create variables for the number of blocks
        if self.nzblocks == -1 or self.nyblocks == -1 or self.nxblocks == -1:
            self.nzblocks = int(round(math.ceil(self.volume_sizes[OR_Z] / self.block_sizes[OR_Z])))
            self.nyblocks = int(round(math.ceil(self.volume_sizes[OR_Y] / self.block_sizes[OR_Y])))
            self.nxblocks = int(round(math.ceil(self.volume_sizes[OR_X] / self.block_sizes[OR_X])))



    def NBlocks(self):
        return (self.nzblocks, self.nyblocks, self.nxblocks)



    def NLabels(self):
        return self.max_label + 1



    def BlockVolume(self):
        return self.block_sizes[OR_Z] * self.block_sizes[OR_Y] * self.block_sizes[OR_X]



    def StartZ(self):
        return self.start_indices[OR_Z]



    def StartY(self):
        return self.start_indices[OR_Y]



    def StartX(self):
        return self.start_indices[OR_X]



    def EndZ(self):
        return self.start_indices[OR_Z] + self.nzblocks



    def EndY(self):
        return self.start_indices[OR_Y] + self.nyblocks



    def EndX(self):
        return self.start_indices[OR_X] + self.nxblocks



    def StartIndices(self):
        return self.start_indices



    def BlockZLength(self):
        return self.block_sizes[OR_Z]



    def BlockYLength(self):
        return self.block_sizes[OR_Y]



    def BlockXLength(self):
        return self.block_sizes[OR_X]



    def BlockSize(self):
        return self.block_sizes



    def VolumeSize(self):
        return self.volume_sizes



    def NVoxels(self):
        nzvoxels = self.block_sizes[OR_Z] * self.nzblocks
        nyvoxels = self.block_sizes[OR_Y] * self.nyblocks
        nxvoxels = self.block_sizes[OR_X] * self.nxblocks

        return nzvoxels * nyvoxels * nxvoxels



    def Resolution(self):
        return self.resolution



    def IndexFromIndices(self, iz, iy, ix):
        zoffset = (iz - self.StartZ())
        yoffset = (iy - self.StartY())
        xoffset = (ix - self.StartX())

        return zoffset * self.nyblocks * self.nxblocks + yoffset * self.nxblocks + xoffset



    def ReadRawSegmentationBlock(self, iz, iy, ix):
        filename = '{}/{:04d}z-{:04d}y-{:04d}x.h5'.format(self.raw_segmentation_path, iz, iy, ix)

        with h5py.File(filename, 'r') as hf:
            data = np.array(hf[list(hf.keys())[0]])

        return data



    def TempDirectory(self):
        return self.tmp_directory



    def TempBlockDirectory(self, iz, iy, ix):
        return '{}/{:04d}z-{:04d}y-{:04d}x'.format(self.tmp_directory, iz, iy, ix)



    def TimingDirectory(self):
        return '{}/timing'.format(self.tmp_directory)



    def SynapseDirectory(self):
        return self.synapse_path



    def SurfacesDirectory(self):
        return self.surfaces_path



    def HoleFillingOutputDirectory(self):
        return self.hole_filling_output_directory



    def SkeletonOutputDirectory(self):
        return self.skeleton_output_directory



    def FiguresDirectory(self):
        return self.figures_directory



    def FigureTitleDescription(self):
        return self.figure_description



    def EvaluationDirectory(self):
        return self.evaluation_directory



    def ReadSegmentationBlock(self, iz, iy, ix):
        # if there was no hole filling computed, read the raw segmentation data
        if self.hole_filling_output_directory == None:
            return self.ReadRawSegmentationBlock(iz, iy, ix)
        # otherwise read in the hole filled output
        filename = '{}/{:04d}z-{:04d}y-{:04d}x.h5'.format(self.hole_filling_output_directory, iz, iy, ix)

        with h5py.File(filename, 'r') as hf:
            data = np.array(hf[list(hf.keys())[0]])

        return data



    def ReadSomataBlock(self, iz, iy, ix):
        # return no soma if it does not exist
        if self.somata_path == None:
            return None
        # otherwise read in the soma file
        filename = '{}/{:04d}z-{:04d}y-{:04d}x.h5'.format(self.somata_path, iz, iy, ix)

        with h5py.File(filename, 'r') as hf:
            data = np.array(hf[list(hf.keys())[0]])

        return data



    def SomataDownsampleRate(self):
        return self.somata_downsample_rate



    def LocalIndicesToGlobalIndex(self, iz, iy, ix, block_index):
        # get the coordinates in global space
        global_iz = iz + block_index[OR_Z] * self.block_sizes[OR_Z]
        global_iy = iy + block_index[OR_Y] * self.block_sizes[OR_Y]
        global_ix = ix + block_index[OR_X] * self.block_sizes[OR_X]

        # convert to global index
        return global_iz * self.volume_sizes[OR_Y] * self.volume_sizes[OR_X] + global_iy * self.volume_sizes[OR_X] + global_ix



    def LocalIndicesToIndex(self, iz, iy, ix):
        # return an index from the indices
        return iz * self.block_sizes[OR_Y] * self.block_sizes[OR_X] + iy * self.block_sizes[OR_X] + ix



    def LocalIndexToIndices(self, iv):
        # get the coordinates in local space
        iz = iv // (self.block_sizes[OR_Y] * self.block_sizes[OR_X])
        iy = (iv - iz * self.block_sizes[OR_Y] * self.block_sizes[OR_X]) // self.block_sizes[OR_X]
        ix = iv % self.block_sizes[OR_X]

        return (iz, iy, ix)



    def GlobalIndicesToIndex(self, iz, iy, ix):
        # return an index from the indices
        return iz * self.volume_sizes[OR_Y] * self.volume_sizes[OR_X] + iy * self.volume_sizes[OR_X] + ix



    def GlobalIndexToIndices(self, iv):
        # get the coordinates in global space
        iz = iv // (self.volume_sizes[OR_Y] * self.volume_sizes[OR_X])
        iy = (iv - iz * self.volume_sizes[OR_Y] * self.volume_sizes[OR_X]) // self.volume_sizes[OR_X]
        ix = iv % self.volume_sizes[OR_X]

        return (iz, iy, ix)



    def GlobalIndexToLocalIndex(self, iv):
        # get the coordinatese in global space
        global_iz, global_iy, global_ix = self.GlobalIndexToIndices(iv)

        local_iz = global_iz % self.block_sizes[OR_Z]
        local_iy = global_iy % self.block_sizes[OR_Y]
        local_ix = global_ix % self.block_sizes[OR_X]

        return self.LocalIndicesToIndex(local_iz, local_iy, local_ix)



    def LocalIndexToGlobalIndex(self, iv, block_index):
        # get the coordinates in local space
        local_iz, local_iy, local_ix = self.LocalIndexToIndices(iv)

        return self.LocalIndicesToGlobalIndex(local_iz, local_iy, local_ix, block_index)
