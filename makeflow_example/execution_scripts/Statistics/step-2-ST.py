import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.evaluate.statistics import CombineStatistics


if len(sys.argv)!=2:
    raise ValueError(" Scripts needs exactley 1 input arguments (Prefix) ")
else:
    meta_fp = sys.argv[1]

# read in the data for this block
data = ReadMetaData(meta_fp)

# Redirect stdout and stderr
RedirectOutStreams(data, "ST", 2, "all", "all", "all")

# check that beforehand step has executed successfully
for iz in range(data.StartZ(), data.EndZ()):
    for iy in range(data.StartY(), data.EndY()):
        for ix in range(data.StartX(), data.EndX()):
            CheckSuccessFile(data, "ST", 1, iz, iy, ix)

# compute the first step to fill holes in each block
CombineStatistics(data)

# Create and Write Success File
WriteSuccessFile(data, "ST", 2, "all", "all", "all")
