import os
import sys

from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.skeletonize.anchors import SaveAnchorWalls



# read passed arguments
prefix,iz,iy,ix = ReadArguments(sys.argv)

# read in the data for this block
data = ReadMetaData(prefix)

# check that beforehand step has executed successfully
CheckSuccessFile(data.TempDirectory(), "HF", 4, iz, iy, ix)

# users must provide an output directory
assert (not data.SkeletonOutputDirectory() == None)
os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

SaveAnchorWalls(data, iz, iy, ix)

# Create and Write Success File
WriteSuccessFile(data.TempDirectory(), "SK", 1, iz, iy, ix)
