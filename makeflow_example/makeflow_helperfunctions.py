import sys

from blockbased_synapseaware.utilities.constants import *


# function to read in input arguments
# (cannot be used for holefilling step 3 and skeletonize step 4)
def ReadArguments(inp_args):
    if len(inp_args)!=5:
        raise ValueError(" Scripts needs exactley 4 input arguments (Prefix iz iy ix) ")
    else:
        prefix = inp_args[1]
        iz = int(inp_args[2])
        iy = int(inp_args[3])
        ix = int(inp_args[4])

    return prefix,iz,iy,ix

def ReadArguments_Short(inp_args):
    if len(inp_args)!=4:
        raise ValueError(" Scripts needs exactley 3 input arguments (Prefix iz iy) ")
    else:
        prefix = inp_args[1]
        iz = int(inp_args[2])
        iy = int(inp_args[3])

    return prefix,iz,iy

def RedirectOutStreams(data, stage, step, iz, iy, ix):
    stdout_fp = data.MFStdoutDirectory() + "/mf-{}-S{}-out-{}z-{}y-{}x.out".format(stage,step,iz,iy,ix)
    stderr_fp = data.MFStderrDirectory() + "/mf-{}-S{}-out-{}z-{}y-{}x.err".format(stage,step,iz,iy,ix)
    print("redirecting stdout to: " + stdout_fp)
    print("redirecting stderr to: " + stderr_fp)
    sys.stdout = open(stdout_fp, 'w+')
    sys.stderr = open(stderr_fp, 'w+')

# redirect output streams for skeletonize step 4
def RedirectOutStreams_SK_4(data, stage, step, label):
    blocksize = data.BlockSize()
    stdout_fp = data.MFStdoutDirectory() + "/mf-{}-S{}-out-label{}.out".format(stage,step,label)
    stderr_fp = data.MFStderrDirectory() + "/mf-{}-S{}-out-label{}.err".format(stage,step,label)

    sys.stdout = open(stdout_fp, 'w+')
    sys.stderr = open(stderr_fp, 'w+')

# fucntion that takes in parameters of a specific computation step and writes success key to file
# (cannot be used for skeletonize step 4)
def WriteSuccessFile(data, stage, step, iz, iy, ix):
    filepath = data.MFCheckfileDirectory() + "/mf-{}-S{}-out-{}z-{}y-{}x.txt".format(stage,step,iz,iy,ix)
    g = open(filepath, "w+")
    g.write("DONE.")
    g.close

# Write success file for skeletonize step 4
def WriteSuccessFile_SK_4(data, stage, step, label):
    filepath = data.MFCheckfileDirectory() + "/mf-{}-S{}-out-label{}.txt".format(stage,step,label)
    g = open(filepath, "w+")
    g.write("DONE.")
    g.close

# Check success file for skeletonize step 4
def CheckSuccessFile_SK_4(data, stage, step, label):
    filepath = data.MFCheckfileDirectory() + "/mf-{}-S{}-out-label{}.txt".format(stage,step,label)
    inp_file = open(filepath)
    inp_text = inp_file.read()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")

# function that takes in parameters of a specific computation step and checks if step terminated successfully
def CheckSuccessFile(data, stage, step, iz, iy, ix):
    filepath = data.MFCheckfileDirectory() + "/mf-{}-S{}-out-{}z-{}y-{}x.txt".format(stage,step,iz,iy,ix)
    inp_file = open(filepath)
    inp_text = inp_file.read()
    inp_file.close()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")
