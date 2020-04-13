import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.hole_filling.connect import ConnectLabelsAcrossBlocks


# pass arguments
if len(sys.argv)!=5:
    raise ValueError(" Scripts needs exactley 2 input arguments (Prefix iz iy ix) ")
else:
    prefix = sys.argv[1]
    iz = int(sys.argv[2])
    iy = int(sys.argv[3])
    ix = int(sys.argv[4])

# read in the data for this block
data = ReadMetaData(prefix)

inp_file = open(data.TempDirectory() + "mf-HF-S1-out-"+str(iz)+"z.txt")
inp_text = inp_file.read()
inp_file.close()

if inp_text[:6]!="DONE.":
    print(inp_text)
    raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the second step to find adjacencies between borders
ConnectLabelsAcrossBlocks(data, iz, iy, ix)

g = open(data.TempDirectory() + "mf-HF-S2-out-"+str(iz)+"z.txt", "w+")
g.write("DONE.")
g.close
