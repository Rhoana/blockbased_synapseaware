import sys
import os

import blockbased_synapseaware.makeflow_example.makeflow_parameters as mf_param
from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData


if len(sys.argv)!=2:
    raise ValueError(" Scripts needs exactley 1 input argument (meta_filepath) ")
else:
    meta_fp = sys.argv[1]

# read in the data for this block
data = ReadMetaData(meta_fp)

blocksize = data.BlockSize()
checkf_folder = mf_param.checkfile_folder +"/{:04d}x{:04d}x{:04d}/".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z])

## read in all parameters needed
replacements_pipeline = [    ("RAM_HF_S1_S4"  ,mf_param.RAM_HF_S1_S4),
                    ("RAM_HF_S2"     ,mf_param.RAM_HF_S2),
                    ("RAM_HF_S3"     ,mf_param.RAM_HF_S3),
                    ("RAM_SK_S1_S2"  ,mf_param.RAM_SK_S1_S2),
                    ("RAM_SK_S3"     ,mf_param.RAM_SK_S3),
                    ("RAM_SK_S4"     ,mf_param.RAM_SK_S4),
                    ("RAM_SF_S1"     ,mf_param.RAM_SF_S1),
                    ("RAM_SF_S2"     ,mf_param.RAM_SF_S2),

                    ("Z_START"       ,data.StartZ()),
                    ("Y_START"       ,data.StartY()),
                    ("X_START"       ,data.StartX()),
                    ("Z_MAX"         ,data.EndZ()),
                    ("Y_MAX"         ,data.EndY()),
                    ("X_MAX"         ,data.EndX()),

                    ("ID_MAX"        ,data.NLabels()),

                    ("META_FP"       ,meta_fp),
                    ("OUTPUT_DIR"    ,checkf_folder),
                    ("MF_DIR"        ,mf_param.makeflow_directory)]


## create working directory

working_dir             = mf_param.makeflow_directory+"/working_directories/working_dir_{:04d}x{:04d}x{:04d}/".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z])
temp_file_dir           = working_dir+"temp_files/"

os.mkdir(working_dir)
os.mkdir(temp_file_dir)

## read in pipeline template, replace parameters and write to working directory
pipeline_template_fp    = mf_param.makeflow_directory+"pipeline_template.jx"
pipeline_out_fp         = working_dir+"pipeline.jx"

fin = open(pipeline_template_fp, "r")
data = fin.read()
fin.close()

# replace templates in file
for entry in replacements_pipeline:
    template = "@${}$@".format(entry[0])
    replacement = str(entry[1])
    # print("replacing {} by {}".format(template,replacement))
    data = data.replace(template, replacement)

#write file to working directory
fin = open(pipeline_out_fp, "w")
fin.write(data)
fin.close()


# replacements batch job
## read in all parameters needed
job_name = "pipeline_{:04d}x{:04d}x{:04d}".format(blocksize[OR_X],blocksize[OR_Y],blocksize[OR_Z])

replacements_batch = [      ("CLUSTER_PARTITION"    ,mf_param.cluster_partition),
                            ("WORKING_DIR"          ,working_dir),
                            ("TEMP_DIR"             ,temp_file_dir),
                            ("JOB_NAME"             ,job_name),
                            ("JOB_TIME"             ,mf_param.job_time),
                            ("MAX_REMOTE"           ,mf_param.max_remote)]

deploy_template_fp    = mf_param.makeflow_directory+"deploy_template.batch"
deploy_out_fp         = working_dir+"deploy_{}.batch".format(job_name)

fin = open(deploy_template_fp, "r")
data = fin.read()
fin.close()

# replace templates in file
for entry in replacements_batch:
    template = "@${}$@".format(entry[0])
    replacement = str(entry[1])
    # print("replacing {} by {}".format(template,replacement))
    data = data.replace(template, replacement)

# write file to working directory
fin = open(deploy_out_fp, "w")
fin.write(data)
fin.close()
