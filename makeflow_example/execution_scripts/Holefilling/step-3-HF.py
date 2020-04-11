import os
import sys

from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.hole_filling.connect import CombineAssociatedLabels


# pass arguments
if len(sys.argv)!=2:
    raise ValueError(" Script needs exactley 1 input parameter (Prefix) ")
else:
    prefix = sys.argv[1]

# read in the data for this block
data = ReadMetaData(prefix)

for iz in range(data.StartZ(), data.EndZ()):

    out_file_S2 = data.TempDirectory() + "mf-HF-S2-out-"+str(iz)+"z.txt"
    inp_file = open(out_file_S2)
    inp_text = inp_file.read()
    inp_file.close()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!= DONE.)")

# users must provide an output directory
assert (not data.HoleFillingOutputDirectory() == None)
os.makedirs(data.HoleFillingOutputDirectory(), exist_ok=True)

# compute the second step to find adjacencies between borders
CombineAssociatedLabels(data)

g = open(data.TempDirectory() + "mf-HF-S3-out.txt", "w+")
g.write("DONE.")
g.close
