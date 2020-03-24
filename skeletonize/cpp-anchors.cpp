#include <unordered_map>
#include <unordered_set>
#include "PGMImage/PGMImage.h"
#include "cpp-skeletonize.h"




void CppComputeAnchorPoints(const char *lookup_table_directory,
                            const char *tmp_current_directory,
                            const char *tmp_neighbor_directory,
                            long *current_seg,
                            long *neighbor_seg,
                            long input_volume_size[3],
                            long input_block_size[3],
                            long current_block_index[3],
                            char direction)
{
    // update global variables
    for (long iv = 0; iv < NDIMS; ++iv) {
        volume_size[iv] = input_volume_size[iv];
        block_size[iv] = input_block_size[iv];
    }

    // set the y and x resolusions
    long yres = 0;
    long xres = 0;
    long neighbor_block_index[3] = { -1, -1, -1 };

    // get the block index for the neighbor block index
    if (direction == 'z') {
        yres = block_size[OR_Y];
        xres = block_size[OR_X];
        neighbor_block_index[OR_Z] = current_block_index[OR_Z] + 1;
        neighbor_block_index[OR_Y] = current_block_index[OR_Y];
        neighbor_block_index[OR_X] = current_block_index[OR_X];
    }
    if (direction == 'y') {
        yres = block_size[OR_Z];
        xres = block_size[OR_X];
        neighbor_block_index[OR_Z] = current_block_index[OR_Z];
        neighbor_block_index[OR_Y] = current_block_index[OR_Y] + 1;
        neighbor_block_index[OR_X] = current_block_index[OR_X];
    }
    if (direction == 'x') {
        yres = block_size[OR_Z];
        xres = block_size[OR_Y];
        neighbor_block_index[OR_Z] = current_block_index[OR_Z];
        neighbor_block_index[OR_Y] = current_block_index[OR_Y];
        neighbor_block_index[OR_X] = current_block_index[OR_X] + 1;
    }

    // create a new PGMImage for each element in this segment
    long nentries = yres * xres;
    const long depth = 1; // value for the depth of the image (always one)

    // set of all sets
    std::unordered_set<long> labels = std::unordered_set<long>();
    std::unordered_map<long, PGMImage *> images = std::unordered_map<long, PGMImage *>();

    for (long iv = 0; iv < nentries; ++iv) {
        // don't consider background or when the neighbor has a different value
        if (not current_seg[iv]) continue;
        if (not (current_seg[iv] == neighbor_seg[iv])) continue;

        // get the label for this segment
        long label = current_seg[iv];

        // if this label has not been seen yet, update
        if (labels.find(label) == labels.end()) {
            labels.insert(label);
            images[label] = new PGMImage(xres, yres, depth);
        }

        // update the pixel for this image
        images[label]->data[iv] = label;
    }

    // iu_center and iv_center will contain the thinned points (anchors)
    std::unordered_map<long, std::vector<long> > iu_centers = std::unordered_map<long, std::vector<long> >();
    std::unordered_map<long, std::vector<long> > iv_centers = std::unordered_map<long, std::vector<long> >();

    // for each label, thin the overlap
    for (std::unordered_map <long, PGMImage *>::iterator it = images.begin(); it != images.end(); ++it) {
        ThinImage(lookup_table_directory, it->second, iu_centers[it->first], iv_centers[it->first]);
    }

    // get the current and neighbor filename for output
    char current_output_filename[4096];
    snprintf(current_output_filename, 4096, "%s/%c-max-computed-anchor-points.pts", tmp_current_directory, direction);

    char neighbor_output_filename[4096];
    snprintf(neighbor_output_filename, 4096, "%s/%c-min-computed-anchor-points.pts", tmp_neighbor_directory, direction);

    // open file pointers for both output files
    FILE *current_fp = fopen(current_output_filename, "wb");
    if (!current_fp) { fprintf(stderr, "Failed to write to %s\n", current_output_filename); exit(-1); }

    FILE *neighbor_fp = fopen(neighbor_output_filename, "wb");
    if (!neighbor_fp) { fprintf(stderr, "Failed to write to %s\n", neighbor_output_filename); exit(-1); }

    // number of labels shared between the two block surfaces
    long nsegments = iu_centers.size();
    WritePtsFileHeader(current_fp, volume_size, block_size, nsegments);
    WritePtsFileHeader(neighbor_fp, volume_size, block_size, nsegments);

    // calculate the checksums for both the current and neighbor blocks
    long current_checksum = 0;
    long neighbor_checksum = 0;

    // iterate over all labels in the volume
    for (std::unordered_map<long, std::vector<long> >::iterator it = iu_centers.begin(); it != iu_centers.end(); ++it) {
        long label = it->first;
        long nanchors = iu_centers[label].size();

        // write the number of labels and anchors for both files
        if (fwrite(&label, sizeof(long), 1, current_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", current_output_filename); exit(-1); }
        if (fwrite(&label, sizeof(long), 1, neighbor_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", neighbor_output_filename); exit(-1); }

        if (fwrite(&nanchors, sizeof(long), 1, current_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", current_output_filename); exit(-1); }
        if (fwrite(&nanchors, sizeof(long), 1, neighbor_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", neighbor_output_filename); exit(-1); }

        // create arrays for the local locations of the anchors points
        long *current_local_indices = new long[nanchors];
        long *neighbor_local_indices = new long[nanchors];
        long *current_global_indices = new long[nanchors];
        long *neighbor_global_indices = new long[nanchors];

        // iterate over all anchors and get correct global and local linear indices
        for (long ii = 0; ii < nanchors; ++ii) {
            // location variables to be updated later
            long iz = 0;
            long iy = 0;
            long ix = 0;

            long local_index, global_index;

            // get the coordinate along the wall
            long iv = iv_centers[label][ii];
            long iu = iu_centers[label][ii];

            // save the results for the current block
            if (direction == 'z') {
                iz = block_size[OR_Z] - 1;
                iy = iv;
                ix = iu;
            }
            if (direction == 'y') {
                iz = iv;
                iy = block_size[OR_Y] - 1;
                ix = iu;
            }
            if (direction == 'x') {
                iz = iv;
                iy = iu;
                ix = block_size[OR_X] - 1;
            }

            // get the local and global index for the current wall
            local_index = LocalIndicesToIndex(iz, iy, ix);
            current_local_indices[ii] = local_index;
            global_index = LocalIndicesToGlobal(iz, iy, ix, current_block_index);
            current_global_indices[ii] = global_index;

            // update the current checksum
            current_checksum += (local_index + global_index);

            // save the results for the neighbor block
            if (direction == 'z') {
                iz = 0;
                iy = iv;
                ix = iu;
            }
            if (direction == 'y') {
                iz = iv;
                iy = 0;
                ix = iu;
            }
            if (direction == 'x') {
                iz = iv;
                iy = iu;
                ix = 0;
            }

            // get the local and global index for the neighbor wall
            local_index = LocalIndicesToIndex(iz, iy, ix);
            neighbor_local_indices[ii] = local_index;
            global_index = LocalIndicesToGlobal(iz, iy, ix, neighbor_block_index);
            neighbor_global_indices[ii] = global_index;

            // update the neighbor checksum
            neighbor_checksum += (local_index + global_index);
        }

        // write the global and then local indices for the current block
        if (fwrite(&(current_global_indices[0]), sizeof(long), nanchors, current_fp) != (unsigned long)nanchors) { fprintf(stderr, "Failed to write to %s.\n", current_output_filename); exit(-1); }
        if (fwrite(&(current_local_indices[0]), sizeof(long), nanchors, current_fp) != (unsigned long)nanchors) { fprintf(stderr, "Failed to write to %s.\n", current_output_filename); exit(-1); }

        // write the global and then local indices for the neighbor block
        if (fwrite(&(neighbor_global_indices[0]), sizeof(long), nanchors, neighbor_fp) != (unsigned long)nanchors) { fprintf(stderr, "Failed to write to %s.\n", neighbor_output_filename); exit(-1); }
        if (fwrite(&(neighbor_local_indices[0]), sizeof(long), nanchors, neighbor_fp) != (unsigned long)nanchors) { fprintf(stderr, "Failed to write to %s.\n", neighbor_output_filename); exit(-1); }

        // free memory
        delete[] current_local_indices;
        delete[] neighbor_local_indices;
        delete[] current_global_indices;
        delete[] neighbor_global_indices;
    }

    if (fwrite(&current_checksum, sizeof(long), 1, current_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", current_output_filename); exit(-1); }
    if (fwrite(&neighbor_checksum, sizeof(long), 1, neighbor_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", neighbor_output_filename); exit(-1); }

    // close files
    fclose(current_fp);
    fclose(neighbor_fp);
}
