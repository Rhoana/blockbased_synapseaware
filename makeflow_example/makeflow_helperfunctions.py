import sys


# function to read in input arguments
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
def WriteSuccessFile(dir, stage, step, iz, iy, ix):

    filepath = dir + "mf-{}-S{}-out-{}z-{}y-{}x.txt".format(stage,step,iz,iy,ix)
    g = open(filepath, "w+")
    g.write("DONE.")
    g.close

# function that takes in parameters of a specific computation step and checks if step terminated successfully
def CheckSuccessFile(dir, stage, step, iz, iy, ix):

    filepath = dir + "mf-{}-S{}-out-{}z-{}y-{}x.txt".format(stage,step,iz,iy,ix)
    inp_file = open(filepath)
    inp_text = inp_file.read()
    inp_file.close()

    if inp_text[:6]!="DONE.":
        print(inp_text)
        raise ValueError("Execution Stopped: Wrong Error Code (!=DONE.)")
