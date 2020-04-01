#include "cpp-skeletonize.h"



// global variables
float resolution[3];
long volume_size[3];
long block_size[3];
long padded_block_size[3];



void WritePtsFileHeader(FILE *fp, long nlabels)
{
    if (fwrite(&(volume_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&(block_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&nlabels, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
}
