from blockbased_synapseaware.hole_filling.components import FindPerBlockConnectedComponents
from blockbased_synapseaware.hole_filling.connect import ConnectLabelsAcrossBlocks
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.utilities.constants import *



def FillHolesSequentially(prefix):
    # read in the data for this block
    data = ReadMetaData(prefix)

    # get the number of blocks in each dimension
    nblocks = data.NBlocks()

    # compute the first step to fill holes in each block
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                FindPerBlockConnectedComponents(data, iz, iy, ix)

    # compute the second step to find adjacencies between borders
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                ConnectLabelsAcrossBlocks(data, iz, iy, ix)
