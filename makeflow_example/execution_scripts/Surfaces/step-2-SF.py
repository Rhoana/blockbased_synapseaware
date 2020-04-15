import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData
from blockbased_synapseaware.makeflow_example.makeflow_helperfunctions import *

from blockbased_synapseaware.hole_filling.components import FindPerBlockConnectedComponents

if len(sys.argv)!=2:
    raise ValueError(" Scripts needs exactley 1 input arguments (Prefix) ")
else:
    meta_fp = sys.argv[1]

# read in the data for this block
data = ReadMetaData(meta_fp)

# compute the first step to fill holes in each block
CombineSurfaceVoxels(data)
