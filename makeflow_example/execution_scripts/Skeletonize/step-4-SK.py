import os
import sys

from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.skeletonize.refinement import RefineSkeleton



# pass arguments
if len(sys.argv)!=3:
    raise ValueError(" Scripts needs exactley 2 input arguments (Prefix label) ")
else:
    meta_fp = sys.argv[1]
    label = int(sys.argv[2])

# read in the data for this block
data = ReadMetaData(meta_fp)

# Redirect stdout and stderr
RedirectOutStreams_SK_4(data, "SK", 4, label)

for iz in range(data.StartZ(), data.EndZ()):
    for iy in range(data.StartY(), data.EndY()):
        for ix in range(data.StartX(), data.EndX()):

            # check that beforehand step has executed successfully
            CheckSuccessFile(data, "SK", 3, iz, iy, ix)

# users must provide an output directory
assert (not data.SkeletonOutputDirectory() == None)
os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

RefineSkeleton(data,label)

# Create and Write Success File
WriteSuccessFile_SK_4(data, "SK", 4, label)
