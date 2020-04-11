import os
import sys

from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.skeletonize.anchors import ComputeAnchorPoints



# pass arguments
if len(sys.argv)!=3:
    raise ValueError(" Scripts needs exactley 2 input arguments (Prefix iz) ")
else:
    prefix = sys.argv[1]
    iz = int(sys.argv[2])

# read in the data for this block
data = ReadMetaData(prefix)

inp_file = open(data.TempDirectory() + "mf-SK-S1-out-"+str(iz)+"z.txt")
inp_text = inp_file.read()
inp_file.close()

if inp_text[:6]!="DONE.":
    print(inp_text)
    raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")

# users must provide an output directory
assert (not data.SkeletonOutputDirectory() == None)
os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

for iy in range(data.StartY(), data.EndY()):
    for ix in range(data.StartX(), data.EndX()):
        ComputeAnchorPoints(data, iz, iy, ix)

g = open(data.TempDirectory() + "mf-SK-S2-out-"+str(iz)+"z.txt", "w+")
g.write("DONE.")
g.close
