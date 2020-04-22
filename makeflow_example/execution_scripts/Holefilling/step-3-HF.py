import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.hole_filling.connect import CombineAssociatedLabels


# pass arguments
# read passed arguments
if len(sys.argv)!=2:
    raise ValueError(" Scripts needs exactley 1 input arguments (Prefix) ")
else:
    meta_fp = sys.argv[1]

# read in the data for this block
data = ReadMetaData(meta_fp)

# Redirect stdout and stderr
RedirectOutStreams(data.BlockSize(), "HF", 3, "all", "all", "all")

# check that beforehand step has executed successfully
for iz in range(data.StartZ(), data.EndZ()):
    for iy in range(data.StartY(), data.EndY()):
        for ix in range(data.StartX(), data.EndX()):
            CheckSuccessFile(data.BlockSize(), "HF", 2, iz, iy, ix)

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the second step to find adjacencies between borders
CombineAssociatedLabels(data)

# Create and Write Success File
WriteSuccessFile(data.BlockSize(), "HF", 3, "all", "all", "all")
