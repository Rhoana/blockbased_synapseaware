#ifndef __CPP_SKELETONIZE__
#define __CPP_SKELETONIZE__

// universal includes
#include <set>
#include <map>
#include <vector>
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>



// universal variables and functions
#define OR_Z 0
#define OR_Y 1
#define OR_X 2
#define NDIMS 3

#define SOMATA_DOWNSAMPLE_RATE 8



// global variables
extern float resolution[3];
extern long volume_size[3];
extern long block_size[3];
extern long padded_block_size[3];
extern std::set<long> labels_in_block;
extern std::map<long, std::set<long> > fixed_points;
extern std::map<long, std::map<long, char> > segments;




void CppComputeAnchorPoints(const char *lookup_table_directory,
                            const char *tmp_current_directory,
                            const char *tmp_neighbor_directory,
                            long *current_seg,
                            long *neighbor_seg,
                            long input_volume_size[3],
                            long input_block_size[3],
                            long current_block_index[3],
                            char direction);



void CppTopologicalThinning(const char *lookup_table_directory,
                            const char *tmp_directory,
                            const char *synapse_directory,
                            long *segmentation,
                            long *somata,
                            float input_resolution[3],
                            long input_volume_size[3],
                            long input_block_size[3],
                            long current_block_index[3]);



void CppSkeletonRefinement(const char *tmp_directory,
                           const char *synapse_directory,
                           const char *skeleton_output_directory,
                           long label,
                           float input_resolution[3],
                           long input_volume_size[3],
                           long input_block_size[3],
                           long start_indices[3],
                           long nblocks[3]);



void WritePtsFileHeader(FILE *fp, long nlabels);



int ReadPtsFile(FILE *fp, bool use_local_coordinates, char mapped_value, bool is_fixed_point);



///////////////////////////////////////////////////////////
//// CONVERT AN INDEX INTO A COORDINATE SET OF INDICES ////
///////////////////////////////////////////////////////////

inline void GenericIndexToIndices(long iv, long &iz, long &iy, long &ix, long input_block_size[3])
{
    // convert this generic index to a group of indices
    iz = iv / (input_block_size[OR_Y] * input_block_size[OR_X]);
    iy = (iv - iz * input_block_size[OR_Y] * input_block_size[OR_X]) / input_block_size[OR_X];
    ix = iv % input_block_size[OR_X];
}



inline void LocalIndexToIndices(long iv, long &iz, long &iy, long &ix)
{
    // return this index to indices
    GenericIndexToIndices(iv, iz, iy, ix, block_size);
}



inline void LocalPaddedIndexToPaddedIndices(long iv, long &iz, long &iy, long &ix)
{
    // return this index to indices
    GenericIndexToIndices(iv, iz, iy, ix, padded_block_size);
}



inline void GlobalIndexToIndices(long iv, long &iz, long &iy, long &ix)
{
    // return this index to indices
    GenericIndexToIndices(iv, iz, iy, ix, volume_size);
}



///////////////////////////////////////////////////////////
//// CONVERT A SET OF COORDINATE INDICES INTO AN INDEX ////
///////////////////////////////////////////////////////////

inline long GenericIndicesToIndex(long iz, long iy, long ix, long input_block_size[3])
{
    return iz * input_block_size[OR_Y] * input_block_size[OR_X] + iy * input_block_size[OR_X] + ix;
}



inline long LocalIndicesToIndex(long iz, long iy, long ix)
{
    return GenericIndicesToIndex(iz, iy, ix, block_size);
}



inline long LocalPaddedIndicesToPaddedIndex(long iz, long iy, long ix)
{
    return GenericIndicesToIndex(iz, iy, ix, padded_block_size);
}



inline long GlobalIndicesToIndex(long iz, long iy, long ix)
{
    return GenericIndicesToIndex(iz, iy, ix, volume_size);
}



//////////////////////////////////////////
//// CONVERT INDEX TO A PADDED INDEX  ////
//////////////////////////////////////////

inline long GenericIndexToPaddedIndex(long iv, long input_block_size[3])
{
    // get the local, unpadded indices
    long iz, iy, ix;
    GenericIndexToIndices(iv, iz, iy, ix, input_block_size);

    // pad the indices by 1
    iz += 1;
    iy += 1;
    ix += 1;

    // return the new index with the padded sizes
    return iz * (input_block_size[OR_Y] + 2) * (input_block_size[OR_X] + 2) + iy * (input_block_size[OR_X] + 2) + ix;
}



inline long LocalIndexToPaddedIndex(long iv)
{
    // return the new index with the padded sizes
    return GenericIndexToPaddedIndex(iv, block_size);
}



inline long GlobalIndexToPaddedIndex(long iv)
{
    // return the new index with the padded sizes
    return GenericIndexToPaddedIndex(iv, volume_size);
}



//////////////////////////////////////////
//// CONVERT INDEX TO A PADDED INDEX  ////
//////////////////////////////////////////

inline long GenericPaddedIndexToIndex(long iv, long input_block_size[3])
{
    // get the local padded indices
    long iz = iv / ((input_block_size[OR_Y] + 2) * (input_block_size[OR_X] + 2));
    long iy = (iv - iz * (input_block_size[OR_Y] + 2) * (input_block_size[OR_X] + 2)) / (input_block_size[OR_X] + 2);
    long ix = iv % (input_block_size[OR_X] + 2);

    // decrement the indices by 1
    iz -= 1;
    iy -= 1;
    ix -= 1;

    // return the new index with the padded sizes
    return GenericIndicesToIndex(iz, iy, ix, input_block_size);
}



inline long LocalPaddedIndexToIndex(long iv)
{
    return GenericPaddedIndexToIndex(iv, block_size);
}



inline long GlobalPaddedIndexToIndex(long iv)
{
    return GenericPaddedIndexToIndex(iv, volume_size);
}



//////////////////////////////////////////////////
//// CONVERT BETWEEN LOCAL AND GLOBAL INDICES ////
//////////////////////////////////////////////////

inline long LocalIndicesToGlobalIndex(long iz, long iy, long ix, long block_index[3])
{
    // get the coordinates in global space
    long global_iz = iz + block_index[OR_Z] * block_size[OR_Z];
    long global_iy = iy + block_index[OR_Y] * block_size[OR_Y];
    long global_ix = ix + block_index[OR_X] * block_size[OR_X];

    // convert to global index
    return global_iz * volume_size[OR_Y] * volume_size[OR_X] + global_iy * volume_size[OR_X] + global_ix;
}



inline long GlobalIndexToLocalIndex(long global_iv)
{
    long global_iz, global_iy, global_ix;
    GlobalIndexToIndices(global_iv, global_iz, global_iy, global_ix);

    // local index is mod of block size
    long local_iz = global_iz % block_size[OR_Z];
    long local_iy = global_iy % block_size[OR_Y];
    long local_ix = global_ix % block_size[OR_X];

    // return the local index
    return LocalIndicesToIndex(local_iz, local_iy, local_ix);
}

#endif
