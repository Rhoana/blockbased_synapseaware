import os
import sys

from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.skeletonize.thinning import TopologicalThinning



# read passed arguments
meta_fp,iz,iy,ix = ReadArguments(sys.argv)

# read in the data for this block
data = ReadMetaData(meta_fp)

# check that beforehand step has executed successfully
CheckSuccessFile(data.BlockSize(), "SK", 2, iz, iy, ix)

# users must provide an output directory
assert (not data.SkeletonOutputDirectory() == None)
os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

TopologicalThinning(data, iz, iy, ix)

# Create and Write Success File
WriteSuccessFile(data.BlockSize(), "SK", 3, iz, iy, ix)
