#include "cpp-skeletonize.h"



// global variables
float resolution[3];
long volume_size[3];
long block_size[3];
long padded_block_size[3];
long padded_volume_size[3];
std::unordered_map<long, std::unordered_set<long> > fixed_points;
std::unordered_map<long, std::unordered_map<long, char> > segments;



void WritePtsFileHeader(FILE *fp, long nlabels)
{
    if (fwrite(&(volume_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&(block_size[0]), sizeof(long), 3, fp) != 3) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
    if (fwrite(&nlabels, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write pts header.\n"); exit(-1); }
}



int ReadPtsFile(FILE *fp, bool use_local_coordinates, char mapped_value, bool is_fixed_point)
{
    long input_volume_size[3];
    long input_block_size[3];
    long nneurons;

    // read the header
    if (fread(&(input_volume_size[0]), sizeof(long), 3, fp) != 3) return 0;
    if (fread(&(input_block_size[0]), sizeof(long), 3, fp) != 3) return 0;
    if (fread(&nneurons, sizeof(long), 1, fp) != 1) return 0;

    for (long iv = 0; iv < NDIMS; ++iv) {
        assert (input_volume_size[iv] == volume_size[iv]);
        assert (input_block_size[iv] == block_size[iv]);
    }

    long checksum = 0;

    // go through every nneuron in this block
    for (long iv = 0; iv < nneurons; ++iv) {
        // get the label and number of elements
        long label;
        long nelements;

        if (fread(&label, sizeof(long), 1, fp) != 1) return 0;
        if (fread(&nelements, sizeof(long), 1, fp) != 1) return 0;

        // create an array to read in all elements
        long *elements = new long[nelements];

        // read in global coordinates (unused here)
        if (fread(&(elements[0]), sizeof(long), nelements, fp) != (unsigned long) nelements) return 0;
        for (long ie = 0; ie < nelements; ++ie) {
            // populate segments with global coordinates
            if (not use_local_coordinates) {
                long index = elements[ie];

                // get the padded index
                long padded_index = GlobalIndexToPaddedIndex(index);

                // set the equivalent element in the segments array to the mapped value
                segments[label][padded_index] = mapped_value;
                if (is_fixed_point) fixed_points[label].insert(padded_index);
            }

            checksum += elements[ie];
        }

        // read in local coordinates
        if (fread(&(elements[0]), sizeof(long), nelements, fp) != (unsigned long) nelements) return 0;
        // for each coordinate, get the padded index and mark as must remain
        for (long ie = 0; ie < nelements; ++ie) {
            // populate segments with local coordinates
            if (use_local_coordinates) {
                long index = elements[ie];

                // get the padded index
                long padded_index = LocalIndexToPaddedIndex(index);

                // set the equivalent element in the segments array to the mapped value
                segments[label][padded_index] = mapped_value;
                if (is_fixed_point) fixed_points[label].insert(padded_index);
            }

            checksum += elements[ie];
        }

        // free memory
        delete[] elements;
    }

    // make sure that the checksum matches
    long input_checksum;
    if (fread(&input_checksum, sizeof(long), 1, fp) != 1) return 0;
    assert (checksum == input_checksum);

    // return success
    return 1;
}
