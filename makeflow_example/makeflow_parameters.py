
makeflow_directory  = "/n/pfister_lab2/Lab/tfranzmeyer/exp_code/blockbased_synapseaware/makeflow_example/"
checkfile_folder    = "/n/pfister_lab2/Lab/tfranzmeyer/exp/output_files/check_files/Zebrafinch/"
stdout_folder       = "/n/pfister_lab2/Lab/tfranzmeyer/exp/output_files/stdout_files/Zebrafinch/"
stderr_folder       = "/n/pfister_lab2/Lab/tfranzmeyer/exp/output_files/stderr_files/Zebrafinch/"

blockconsumption = 512*512*512*8/1000/1000

RAM_HF_S1_S4  = int(blockconsumption*3.5*2)
RAM_HF_S2     = int(blockconsumption*0.5*2)
RAM_HF_S3     = int(30000*5)
RAM_SK_S1_S2  = int(blockconsumption*2*2)
RAM_SK_S3     = int(blockconsumption*6*2)
RAM_SK_S4     = int(20000)
RAM_ST_S1     = int(blockconsumption*4*2)
RAM_ST_S2     = int(20000)

cluster_partition = "test"
job_time = "0-00:59"
max_remote = 5
