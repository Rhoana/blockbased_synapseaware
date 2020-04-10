import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.hole_filling.components import FindPerBlockConnectedComponents

# pass arguments
if len(sys.argv)!=3:
    raise ValueError(" Scripts needs exactley 2 input argument (Prefix iz)")
else:
    prefix = sys.argv[1]
    iz = int(sys.argv[2])

# read in the data for this block
data = ReadMetaData(prefix)

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the first step to fill holes in each block
for iy in range(data.StartY(), data.EndY()):
    for ix in range(data.StartX(), data.EndX()):
        FindPerBlockConnectedComponents(data, iz, iy, ix)

g = open(data.TempDirectory() + "mf-HF-S1-out-"+str(iz)+"z.txt", "w+")
g.write("DONE.")
g.close
