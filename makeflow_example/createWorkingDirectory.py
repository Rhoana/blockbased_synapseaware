import sys
import os

from blockbased_synapseaware.makeflow_example.makeflow_parameters import *
from blockbased_synapseaware.utilities.constants import *

if len(sys.argv)!=2:
    raise ValueError(" Scripts needs exactley 1 input argument (meta_filepath) ")

# read in the data for this block
data = ReadMetaData(meta_fp)

## read in all parameters needed
replacements = [    ("RAM_HF_S1_S4"  ,RAM_HF_S1_S4),
                    ("RAM_HF_S2"     ,RAM_HF_S2),
                    ("RAM_HF_S3"     ,RAM_HF_S3),
                    ("RAM_SK_S1_S2"  ,RAM_SK_S1_S2),
                    ("RAM_SK_S3"     ,RAM_SK_S3),
                    ("RAM_SK_S4"     ,RAM_SK_S4),
                    ("RAM_SF_S1"     ,RAM_SF_S1),
                    ("RAM_SF_S2"     ,RAM_SF_S2),

                    ("Z_START"       ,data.StartZ()),
                    ("Y_START"       ,data.StartY()),
                    ("X_START"       ,data.StartX()),
                    ("Z_MAX"         ,data.EndZ()),
                    ("Y_MAX"         ,data.EndY()),
                    ("X_MAX"         ,data.EndX()),

                    ("ID_MAX"        ,data.NLabels()),

                    ("META_FP"       ,meta_fp),
                    ("OUTPUT_DIR"    ,checkfile_folder),
                    ("MF_DIR"        ,makeflow_directory)]

## create working directory
blocksize               = data.BlockSize()
working_dir             = makeflow_directory+"working_dir{:04d}x{:04d}x{:04d}/".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z])
temp_file_dir           = working_dir+"temp_files"

os.mkdir(working_dir)
os.mkdir(temp_file_dir)

## read in pipeline template, replace parameters and write to working directory
pipeline_template_fp    = makeflow_directory+"pipeline_template.jx"
pipeline_out_fp         = working_dir+"pipeline.jx"

fin = open(pipeline_template_fp, "r")
data = fin.read()
fin.close()

# replace templates in file
for entry in replacements:
    template = "@${}$@".format(entry[0])
    replacement = entry[2]
    data = data.replace(template, replacement)

#write file to working directory
fin = open(pipeline_out_fp, "w")
fin.write(data)
fin.close()
