import sys
import os

import blockbased_synapseaware.makeflow_example.makeflow_parameters as mf_param
from blockbased_synapseaware.utilities.constants import *
from blockbased_synapseaware.utilities.dataIO import ReadMetaData


def readArgv(argv_list):

    if len(argv_list)!=2:
        raise ValueError(" Scripts needs exactley 1 input argument (meta_filepath) ")
    else:
        meta_fp = argv_list[1]

    return meta_fp

def replaceStrings(filename_in, filename_out, replacements):

    # read in template file
    fin = open(filename_in, "r")
    data = fin.read()
    fin.close()

    # replace templates in file
    for entry in replacements:
        template = "@${}$@".format(entry[0])
        replacement = str(entry[1])
        # print("replacing {} by {}".format(template,replacement))
        data = data.replace(template, replacement)

    # write file
    fin = open(filename_out, "w")
    fin.write(data)
    fin.close()

def writePipelineFile(working_dir, data, meta_fp):

    ## read in pipeline template, replace parameters and write to working directory
    pipeline_template_fp    = mf_param.makeflow_directory+"pipeline_template.jx"
    pipeline_out_fp         = working_dir+"pipeline.jx"

    checkf_folder = mf_param.checkfile_folder +"/{:04d}x{:04d}x{:04d}/".format(data.BlockSize()[OR_X],data.BlockSize()[OR_Y],data.BlockSize()[OR_Z])

    ## read in all parameters needed
    replacements_pipeline = [    ("RAM_HF_S1_S4"  ,mf_param.RAM_HF_S1_S4),
                        ("RAM_HF_S2"     ,mf_param.RAM_HF_S2),
                        ("RAM_HF_S3"     ,mf_param.RAM_HF_S3),
                        ("RAM_SK_S1_S2"  ,mf_param.RAM_SK_S1_S2),
                        ("RAM_SK_S3"     ,mf_param.RAM_SK_S3),
                        ("RAM_SK_S4"     ,mf_param.RAM_SK_S4),
                        ("RAM_ST_S1"     ,mf_param.RAM_ST_S1),
                        ("RAM_ST_S2"     ,mf_param.RAM_ST_S2),

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

    # replace strings and write file
    replaceStrings(pipeline_template_fp, pipeline_out_fp, replacements_pipeline)

def writeBatchFile(working_dir, data):

    # replacements batch job
    job_name = "pipeline_{:04d}x{:04d}x{:04d}".format(data.BlockSize()[OR_X],data.BlockSize()[OR_Y],data.BlockSize()[OR_Z])

    deploy_template_fp    = mf_param.makeflow_directory+"deploy_template.batch"
    deploy_out_fp         = working_dir+"deploy_{}.batch".format(job_name)

    replacements_batch = [      ("CLUSTER_PARTITION"    ,mf_param.cluster_partition),
                                ("WORKING_DIR"          ,working_dir),
                                ("TEMP_DIR"             ,temp_file_dir),
                                ("JOB_NAME"             ,job_name),
                                ("JOB_TIME"             ,mf_param.job_time),
                                ("MAX_REMOTE"           ,mf_param.max_remote)]

    # replace strings and write file
    replaceStrings(deploy_template_fp, deploy_out_fp, replacements_batch)

if __name__ == "__main__":

    # read meta filepath
    meta_fp = readArgv(sys.argv)

    # read in the data for this block
    data = ReadMetaData(meta_fp)

    # create working directory and directory for temporary makeflow files
    working_dir = mf_param.makeflow_directory+"/working_directories/working_dir_{:04d}x{:04d}x{:04d}/".format(data.BlockSize()[OR_X],data.BlockSize()[OR_Y],data.BlockSize()[OR_Z])
    temp_file_dir = working_dir+"temp_files/"

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    if not os.path.exists(temp_file_dir):
        os.mkdir(temp_file_dir)

    # write pipeline and batch deploy file
    writePipelineFile(working_dir, data, meta_fp)
    writeBatchFile(working_dir, data)
