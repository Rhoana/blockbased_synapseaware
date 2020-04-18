import sys

from blockbased_synapseaware.makeflow_example.makeflow_parameters import *
from blockbased_synapseaware.utilities.constants import *

# function to read in input arguments
# (cannot be used for holefilling step 3 and skeletonize step 4)
def ReadArguments(inp_args):
    if len(inp_args)!=5:
        raise ValueError(" Scripts needs exactley 2 input arguments (Prefix iz iy ix) ")
    else:
        prefix = inp_args[1]
        iz = int(inp_args[2])
        iy = int(inp_args[3])
        ix = int(inp_args[4])

    return prefix,iz,iy,ix

# fucntion that takes in parameters of a specific computation step and writes success key to file
# (cannot be used for skeletonize step 4)
def WriteSuccessFile(blocksize, stage, step, iz, iy, ix):

    filepath = checkfile_folder + "{}x{}x{}/mf-{}-S{}-out-{}z-{}y-{}x.txt".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z],stage,step,iz,iy,ix)
    g = open(filepath, "w+")
    g.write("DONE.")
    g.close

# Write success file for skeletonize step 4
def WriteSuccessFile_SK_4(blocksize, stage, step, label):

    filepath = checkfile_folder + "{}x{}x{}/mf-{}-S{}-out-label{}.txt".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z],stage,step,label)
    g = open(filepath, "w+")
    g.write("DONE.")
    g.close

# Check success file for skeletonize step 4
def CheckSuccessFile_SK_4(blocksize, stage, step, label):

    filepath = checkfile_folder + "{}x{}x{}/mf-{}-S{}-out-label{}.txt".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z],stage,step,label)
    inp_file = open(filepath)
    inp_text = inp_file.read()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")

# function that takes in parameters of a specific computation step and checks if step terminated successfully
def CheckSuccessFile(blocksize, stage, step, iz, iy, ix):

    filepath = checkfile_folder + "{}x{}x{}/mf-{}-S{}-out-{}z-{}y-{}x.txt".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z],stage,step,iz,iy,ix)
    inp_file = open(filepath)
    inp_text = inp_file.read()
    inp_file.close()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")
