import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.hole_filling.components import FindPerBlockConnectedComponents

# read passed arguments
meta_fp,iz,iy = ReadArguments_Short(sys.argv)

# read in the data for this block
data = ReadMetaData(meta_fp)

# iterate over x blocks, preventing very short jobs on the cluster
for ix in range(data.StartX(), data.EndX()):

    # Redirect stdout and stderr
    RedirectOutStreams(data, "HF", 1, iz, iy, ix)

    # users must provide an output directory
    assert (not data.HoleFillingOutputDirectory() == None)
    os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

    # compute the first step to fill holes in each block
    FindPerBlockConnectedComponents(data, iz, iy, ix)

    # Create and Write Success File
    WriteSuccessFile(data, "HF", 1, iz, iy, ix)
