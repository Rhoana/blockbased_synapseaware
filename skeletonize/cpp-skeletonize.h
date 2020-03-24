#ifndef __CPP_SKELETONIZE__
#define __CPP_SKELETONIZE__

// universal includes
#include <stdio.h>
#include <stdlib.h>



// universal variables and functions
#define OR_Z 0
#define OR_Y 1
#define OR_X 2
#define NDIMS 3



// global variables
extern long volume_size[3];
extern long block_size[3];




void CppComputeAnchorPoints(const char *lookup_table_directory,
                            const char *tmp_current_directory,
                            const char *tmp_neighbor_directory,
                            long *current_seg,
                            long *neighbor_seg,
                            long input_volume_size[3],
                            long input_block_size[3],
                            long current_block_index[3],
                            char direction);



void WritePtsFileHeader(FILE *fp, long volume_size[3], long block_size[3], long nlabels);




inline long LocalIndicesToIndex(long iz, long iy, long ix)
{
    return iz * block_size[OR_Y] * block_size[OR_X] + iy * block_size[OR_X] + ix;
}



inline long LocalIndicesToGlobal(long iz, long iy, long ix, long block_index[3])
{
    // get the coordinates in global space
    long global_iz = iz + block_index[OR_Z] * block_size[OR_Z];
    long global_iy = iy + block_index[OR_Y] * block_size[OR_Y];
    long global_ix = ix + block_index[OR_X] * block_size[OR_X];

    // convert to global index
    return global_iz * volume_size[OR_Y] * volume_size[OR_X] + global_iy * volume_size[OR_X] + global_ix;
}



inline long GlobalIndicesToIndex(long iz, long iy, long ix)
{
    return iz * volume_size[OR_Y] * volume_size[OR_X] + iy * volume_size[OR_X] + ix;
}



#endif
