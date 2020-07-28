import os



from blockbased_synapseaware.skeletonize.anchors import ComputeAnchorPoints, SaveAnchorWalls
from blockbased_synapseaware.skeletonize.thinning import TopologicalThinning
from blockbased_synapseaware.skeletonize.refinement import RefineSkeleton
from blockbased_synapseaware.utilities.dataIO import ReadMetaData



def SkeletonizeSequentially(meta_filename):
    # read in the data for this block
    data = ReadMetaData(meta_filename)

    # users must provide an output directory
    assert (not data.SkeletonOutputDirectory() == None)
    os.makedirs(data.SkeletonOutputDirectory(), exist_ok=True)

    # compute the first step to save the walls of each file
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                SaveAnchorWalls(data, iz, iy, ix)

    # compute the second step to find the anchors between blocks
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                ComputeAnchorPoints(data, iz, iy, ix)

    # compute the third step to thin each block independently
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                TopologicalThinning(data, iz, iy, ix)

    # compute the fourth step to refine the skeleton
    for label in range(1, data.NLabels()):
        RefineSkeleton(data, label)
