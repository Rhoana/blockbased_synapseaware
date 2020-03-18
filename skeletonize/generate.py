import os



from blockbased_synapseaware.skeletonize.anchors import SaveAnchorWalls
from blockbased_synapseaware.utilities.dataIO import ReadMetaData



def SkeletonizeSequentially(prefix):
    # read in the data for this block
    data = ReadMetaData(prefix)

    # users must provide an output directory
    assert (not data.SkeletonOutputDirectory() == None)
    os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

    # compute the first step to save the walls of each file
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                SaveAnchorWalls(data, iz, iy, ix)
