import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.evaluate.statistics import CalculatePerBlockStatistics

# read passed arguments
meta_fp,iz,iy,ix = ReadArguments(sys.argv)

# read in the data for this block
data = ReadMetaData(meta_fp)

# Redirect stdout and stderr
RedirectOutStreams(data.BlockSize(), "ST", 1, iz, iy, ix)

for label in range(data.NLabels()):
        # check that beforehand step has executed successfully
        CheckSuccessFile_SK_4(data.BlockSize(), "SK", 4, label)

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the first step to fill holes in each block
CalculatePerBlockStatistics(data, iz, iy, ix)

# Create and Write Success File
WriteSuccessFile(data.BlockSize(), "ST", 1, iz, iy, ix)
