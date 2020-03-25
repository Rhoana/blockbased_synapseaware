import os
import sys
import math
import h5py


import numpy as np



from blockbased_synapseaware.utilities.constants import *



class MetaData:
    def __init__(self, prefix):
        self.prefix = prefix
        # create default variable values
        self.raw_segmentation_path = None
        self.tmp_directory = None
        self.block_sizes = None
        self.volume_sizes = None
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
        # place to save the generated skeletons
        self.skeleton_output_directory = None
        self.resolution = None

        # open the meta file and read in requisite information
        with open('meta/{}.meta'.format(prefix), 'r') as fd:
            lines = [line for line in fd.readlines() if line.strip()]

            # meta files have pairs of lines with comments and values
            for iv in range(0, len(lines), 2):
                comment = lines[iv].strip()
                value = lines[iv + 1].strip()

                if comment == '# path to raw segmentations':
                    self.raw_segmentation_path = value
                elif comment == '# temporary files directory':
                    self.tmp_directory = value
                elif comment == '# block size':
                    block_sizes = value.split('x')
                    self.block_sizes = (int(block_sizes[OR_Z]), int(block_sizes[OR_Y]), int(block_sizes[OR_X]))
                elif comment == '# volume size':
                    volume_sizes = value.split('x')
                    self.volume_sizes = (int(volume_sizes[OR_Z]), int(volume_sizes[OR_Y]), int(volume_sizes[OR_X]))
                elif comment == '# start block indices':
                    start_indices = value.split(',')
                    self.start_indices = (int(start_indices[OR_Z]), int(start_indices[OR_Y]), int(start_indices[OR_X]))
                elif comment == '# number of blocks to skeletonize':
                    nblocks = value.split(',')
                    self.nzblocks = int(nblocks[OR_Z])
                    self.nyblocks = int(nblocks[OR_Y])
                    self.nxblocks = int(nblocks[OR_X])
                elif comment == '# hole filling output directory':
                    self.hole_filling_output_directory = value
                elif comment == '# path to synapses':
                    self.synapse_path = value
                elif comment == '# path to somata':
                    self.somata_path = value
                elif comment == '# skeleton output directory':
                    self.skeleton_output_directory = value
                elif comment == '# resolution in nm':
                    resolutions = value.split('x')
                    self.resolution = (float(resolutions[OR_Z]), float(resolutions[OR_Y]), float(resolutions[OR_X]))
                else:
                    sys.stderr.write('Unrecognized meta file attribute: {}\n'.format(comment))
                    exit(-1)

        # make sure important values are initialized
        assert (not self.raw_segmentation_path == None)
        assert (not self.tmp_directory == None)
        assert (not self.block_sizes == None)
        assert (not self.volume_sizes == None)
        assert (not self.synapse_path == None)
        assert (not self.resolution == None)

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
        return '{}/{}/'.format(self.tmp_directory, self.prefix)



    def TempComponentsDirectory(self, iz, iy, ix):
        return '{}/{}/{:04d}z-{:04d}y-{:04d}x'.format(self.tmp_directory, self.prefix, iz, iy, ix)



    def HoleFillingOutputDirectory(self):
        return self.hole_filling_output_directory



    def SkeletonOutputDirectory(self):
        return self.skeleton_output_directory



    def ReadSegmentationBlock(self, iz, iy, ix):
        # if there was no hole filling computed, read the raw segmentation data
        if self.hole_filling_output_directory == None:
            return ReadRawSegmentationBlock(self, iz, iy, ix)
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
