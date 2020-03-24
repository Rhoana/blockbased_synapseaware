#include "cpp-skeletonize.h"



// global variables used by all files
long volume_size[3];
long block_size[3];



void WritePtsFileHeader(FILE *fp, long volume_size[3], long block_size[3], long nlabels)
{
    if (fwrite(&(volume_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&(block_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&nlabels, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
}
