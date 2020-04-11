import os
import sys

from blockbased_synapseaware.utilities.dataIO import ReadMetaData

from blockbased_synapseaware.skeletonize.refinement import RefineSkeleton



# pass arguments
if len(sys.argv)!=3:
    raise ValueError(" Scripts needs exactley 2 input arguments (Prefix label) ")
else:
    prefix = sys.argv[1]
    label = int(sys.argv[2])

# read in the data for this block
data = ReadMetaData(prefix)

for iz in range(data.StartZ(), data.EndZ()):

    out_file_S3 = data.TempDirectory() + "mf-SK-S3-out-"+str(iz)+"z.txt"
    inp_file = open(out_file_S3)
    inp_text = inp_file.read()
    inp_file.close()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!= DONE.)")

# users must provide an output directory
assert (not data.SkeletonOutputDirectory() == None)
os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

RefineSkeleton(data,label)

g = open(data.TempDirectory() + "mf-SK-S4-out-"+str(label)+"label.txt", "w+")
g.write("DONE.")
g.close
