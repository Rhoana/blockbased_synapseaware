import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.hole_filling.mapping import RemoveHoles

# read passed arguments
prefix,iz,iy,ix = ReadArguments(sys.argv)

# read in the data for this block
data = ReadMetaData(prefix)

# check that beforehand step has executed successfully
CheckSuccessFile(data.TempDirectory(), "HF", 3, "all", "all", "all")

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

RemoveHoles(data, iz, iy, ix)

# Create and Write Success File
WriteSuccessFile(data.TempDirectory(), "HF", 4, iz, iy, ix)
