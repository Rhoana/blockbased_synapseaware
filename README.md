# Block-Based Synapse Aware Skeleton Generation
This README is under contruction. It will be completed once this work is published.
## Methodology Overview

![](https://github.com/Rhoana/blockbased_synapseaware/blob/master/figures/Figure1.png) **Figure 1** Left: Small example input segmentation, different colors indicating different labels. Right: Output centerlines (skeletons) for a small part of a single neuron. Neuron shown in green, centerlines in black. Synapses are indicated by the balck spheres. Black boxes show zoom ins.

This repository provides an end-to-end pipeline for skeleton generation of neural circuits. As input, it takes segmented neural data and the locations and labels of all synapses present in the volume. The input volume can be of almost arbitrary size, as it can be saved and processed in blocks, using a MapReduce approach. Additionally, a somata (cell body) segmentation can be utilized to speed up computation and improve skeleton quality.
The pipeline consists of two main stages: Holefilling and Skeletonization.
### Holefilling
Automatically segmented neural circuits typically include multiple holes of various sizes. These holes are cavities/bubbles within a neuron, caused by false negative segmentations. As neurons generally have a genus of 0, holes are filled in a preprocessing step. This not only improves the quality of the segmentation and therefore also of the final skeletons, but also accelerates the subsequent skeletonization process.
### Skeletonization
Skeletonization takes as input the filled segmentation and the location of all synapses present in the volume. Additionally, a somata segmentation can be provided. Using this somata segmentation, somata can be masked out in the computation, which reduces the computational demand.  In a first step, so called “anchor points” on all block surfaces are computed, guaranteeing skeleton continuity over block boundaries. Also, if provided, the outer surface of each soma is detected and fixed, forcing skeletons to arise from the soma surface. <br /> Anchorpoints, somata surface points and the already known synapses are then set as fixpoints in the subsequent topological thinning step.  During topological thinning, neuron surfaces are gradually eroded, while always preserving topology. <br /> The skeleton is found when there are no more points (voxels) left that can be eroded, either because a potential voxel is a fixpoint or because its removal would lead to a change in topology. <br /> The skeletons are at first computed for each label present in each block and saved as an intermediate result.   In a final step, the global skeleton for each label is assembled from the various segments resulting from different blocks. Next, a refinement step is executed and the final skeletons for each label are saved as pointfiles.
## Installation

## File Types
### Point Files
Point coordinates (x,y,z) are generally saved as linear indices. 
All points are saved with both their local and global linear indices. The local index gives the position in the coordinate system of the block that the point lies in, while the global index gives the position in the volume coordinate system.
The conversion functions from coordinates to indices, as well as from local to global are given in *data_structures/meta_data.py*.   
Point files are saved in binary format, with a size of 8 bits per entry.
Each point file contains a header which specifies the volumesize, blocksize and number of labels saved in this point file.
Below, local and global indices for all points are written, topped by the accoring label.
The last entry in the file is a checksum. This checksum is computed as the sum over all global and local indices written to this file, irrespective of the label.
An exact description of the point file structure is given in (TODO add visual).
### Segmentation Files
The segmentation is generally saved as a 3D array, where each entry corresponds to a voxel, whose size is given by the data resolution, which is specified in the meta file under *# resolution in nm (x, y, z)*. Entries in this array are unsigned integers of 64 bit size. If an entry is 0, it indicates that at the respective position there is no neuron present, which is referred to as background. An entry larger than 0 indicates that the respective voxel is occupied by a neuron with the corresponding label. Logically, each voxel can only be occupied by a single neuron. Segmentation data are expected to have an axes ordering of z,y,x.
## Parameter Specification
All parameters needed are specified in the meta file. An example meta file is given in (TODO add example meta file and explain all parameters needed).
## Input Files
### Meta File
The meta file must be adjusted according to the given folder structure and data specifications. Parameters are explained in *Parameter Specification*.
### Neurite Segmentation
The segmentation volume can be cut in multiple blocks, which allows for volumes of almost arbitrary size. Concatenating all blocks along the respective axes must yield the original volume. Each block is saved as an h5 file, using gzip compression. 
The folder location for the raw segmentation must be given in the meta file, under *# path to raw segmentation*.
   The file for each block must be named as following: *‘{:04d}z-{:04d}y-{:04d}x.h5'.format(iz, iy, ix)*, where iz corresponds to the block index in z direction, iy to the block index in y direction and ix to the block index in x direction.
E.g., the segmentation for the block with indices iz=5, iy=10 and ix=4 must be named *‘0005z-0010y-0004x.h5’*.
### Synapse Locations
Synapse position are saved using point files. For each synapse, its 3D coordinate and its label must be known. Point files are explained in section *File Types/ Point Files*.
The folder in which the synapse files are saved must be given under *# path to synapses* in the meta file.
Files are named similar to segmentation files, but with a *.pts* ending. Hence, the point file for all synapses present in the block with indices iz=44, iy=3 and ix=2 must be named *‘0044z-0003y-0002x.pts’*.
### Somata Segmentation
The Somata segmentation is saved very similarly to the input segmentation of neurite data. All somata voxels are labeled with their respective ID while all remaining voxels are labeled 0. The somata segmentation can be saved with a downsampled resolution, where the downsampling factor has to be given under *# somata downsample rate* in the meta file. The folder in which the somata segmentation files are saved must be specified under *# path to somata* in the meta file. The somata segmentation files are then named equivalently to the input segmentation files, as specified in *Input Files/ Neurite Segmentation*. Somata detection can be skipped by omitting the sections *# somata downsample rate* and *# path to somata* in the meta file.
## Output Files
### Skeletons
Skeletons are written to the folder which is specified under *# skeleton output directory* in the meta file. One skeleton file is written for each label present in the volume. Each skeleton file is a point file.

## Execution
### Bash
TODO
### Parallelization on SLURM cluster
TODO
