import os

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.hole_filling.connect import CombineAssociatedLabels

# read in the data for this block
data = ReadMetaData(prefix)

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the second step to find adjacencies between borders
for iz in range(data.StartZ(), data.EndZ()):
    for iy in range(data.StartY(), data.EndY()):
        for ix in range(data.StartX(), data.EndX()):
            ConnectLabelsAcrossBlocks(data, iz, iy, ix)
