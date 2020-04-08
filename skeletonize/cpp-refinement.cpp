#include "cpp-skeletonize.h"
#include "cpp-MinBinaryHeap.h"



// struct for Dijkstra's algorithm
struct DijkstraData {
    long iv;
    DijkstraData *prev;
    float distance;
    bool visited;
};



static int WriteTempPtsFile(FILE *fp, std::vector<long> &elements, long label)
{
    WritePtsFileHeader(fp, 1);

    // write the number of neurons and points
    long npoints = elements.size();
    if (fwrite(&label, sizeof(long), 1, fp) != 1) return 0;
    if (fwrite(&npoints, sizeof(long), 1, fp) != 1) return 0;

    long checksum = 0;
    long *global_indices = new long[elements.size()];
    long *local_indices = new long[elements.size()];

    for (long iv = 0; iv < npoints; ++iv) {
        long global_index = elements[iv];
        long local_index = GlobalIndexToLocalIndex(global_index);

        global_indices[iv] = global_index;
        local_indices[iv] = local_index;

        checksum += (global_indices[iv] + local_indices[iv]);
    }

    if (fwrite(&(global_indices[0]), sizeof(long), npoints, fp) != (unsigned long) npoints) return 0;
    if (fwrite(&(local_indices[0]), sizeof(long), npoints, fp) != (unsigned long) npoints) return 0;

    if (fwrite(&checksum, sizeof(long), 1, fp) != 1) return 0;

    // free memory
    delete[] global_indices;
    delete[] local_indices;

    // return success
    return 1;
}



static void WriteTempFiles(const char *tmp_directory, long label)
{
    // create vectors for surfaces, synapses, and skeletons
    std::vector<long> somata_surface = std::vector<long>();
    std::vector<long> synapses = std::vector<long>();
    std::vector<long> skeleton = std::vector<long>();

    std::map<long, char>::iterator it;
    for (it = segments[label].begin(); it != segments[label].end(); ++it) {
        long padded_index = it->first;
        long global_index = GlobalPaddedIndexToIndex(padded_index);

        if (it->second == 1) skeleton.push_back(global_index);
        if (it->second == 3) synapses.push_back(global_index);
        if (it->second == 4) somata_surface.push_back(global_index);
    }

    // write temp points files for synapses, skeletons, and somata surfaces for this label
    char tmp_synapse_filename[4096];
    snprintf(tmp_synapse_filename, 4096, "%s/synapses/%016ld.pts", tmp_directory, label);

    // open file
    FILE *synapse_fp = fopen(tmp_synapse_filename, "wb");
    if (!synapse_fp) { fprintf(stderr, "Failed to write to %s.\n", tmp_synapse_filename); exit(-1); }

    // write the synapses file
    if (!WriteTempPtsFile(synapse_fp, synapses, label)) { fprintf(stderr, "Failed to write to %s.\n", tmp_synapse_filename); exit(-1); }

    // close file
    fclose(synapse_fp);

    char tmp_somata_surface_filename[4096];
    snprintf(tmp_somata_surface_filename, 4096, "%s/somata_surfaces/%016ld.pts", tmp_directory, label);

    // open file
    FILE *somata_fp = fopen(tmp_somata_surface_filename, "wb");
    if (!somata_fp) { fprintf(stderr, "Failed to write to %s.\n", tmp_somata_surface_filename); exit(-1); }

    // write the synapses file
    if (!WriteTempPtsFile(somata_fp, somata_surface, label)) { fprintf(stderr, "Failed to write to %s.\n", tmp_somata_surface_filename); exit(-1); }

    // close file
    fclose(somata_fp);

    char tmp_skeleton_filename[4096];
    snprintf(tmp_skeleton_filename, 4096, "%s/skeletons/%016ld.pts", tmp_directory, label);

    // open file
    FILE *skeleton_fp = fopen(tmp_skeleton_filename, "wb");
    if (!somata_fp) { fprintf(stderr, "Failed to write to %s.\n", tmp_skeleton_filename); exit(-1); }

    // write the synapses file
    if (!WriteTempPtsFile(skeleton_fp, skeleton, label)) { fprintf(stderr, "Failed to write to %s.\n", tmp_skeleton_filename); exit(-1); }

    // close file
    fclose(skeleton_fp);
}



static void RunDijkstrasAlgorithm(const char *skeleton_output_directory, long label)
{
    // a mapping from linear global indices to indices in a dijkstra array data structure
    std::map<long, long> dijkstra_map = std::map<long, long>();

    long nvoxels = segments[label].size();
    DijkstraData *voxel_data = new DijkstraData[nvoxels];
    if (!voxel_data) exit(-1);

    printf("  Points Before Refinement: %ld\n", nvoxels);

    // create a min binary heap
    DijkstraData tmp;
    MinBinaryHeap<DijkstraData *> voxel_heap(&tmp, &(tmp.distance), nvoxels);

    // create sufficiently large value for infinity
    long infinity = padded_volume_size[OR_Z] * padded_volume_size[OR_Z] + padded_volume_size[OR_Y] * padded_volume_size[OR_Y] + padded_volume_size[OR_X] * padded_volume_size[OR_X];

    // initialize all data
    long index = 0;
    std::map<long, char>::iterator it;
    for (it = segments[label].begin(); it != segments[label].end(); ++it, ++index) {
        voxel_data[index].iv = it->first;               // voxel index
        voxel_data[index].prev = NULL;
        voxel_data[index].distance = infinity;
        voxel_data[index].visited = false;
        dijkstra_map[it->first] = index;

        // somata surface points are anchor points
        // a designated synapse receives a value of 2 and is also source
        if (not (it->second % 2)) {
            // insert the source into the heap
            voxel_data[index].distance = 0.0;
            voxel_data[index].visited = true;
            voxel_heap.Insert(index, &(voxel_data[index]));
        }
    }

    long voxel_index;
    while (!voxel_heap.IsEmpty()) {
        DijkstraData *current = voxel_heap.DeleteMin();
        voxel_index = current->iv;

        // visit all 26 neighbors of this index
        long iz, iy, ix;
        GlobalPaddedIndexToPaddedIndices(voxel_index, iz, iy, ix);

        for (long iw = iz - 1; iw <= iz + 1; ++iw) {
            for (long iv = iy - 1; iv <= iy + 1; ++iv) {
                for (long iu = ix - 1; iu <= ix + 1; ++iu) {
                    // do not iterate over itself
                    if (iw == iz and iv == iy and iu == ix) continue;

                    // get the linear index for this voxel
                    long neighbor_index = GlobalPaddedIndicesToPaddedIndex(iw, iv, iu);

                    // skip if background
                    if (!segments[label][neighbor_index]) continue;

                    // get the corresponding neighbor data
                    long dijkstra_index = dijkstra_map[neighbor_index];
                    DijkstraData *neighbor_data = &(voxel_data[dijkstra_index]);

                    // find the distance between these two voxels
                    long deltaz = resolution[OR_Z] * (iw - iz);
                    long deltay = resolution[OR_Y] * (iv - iy);
                    long deltax = resolution[OR_X] * (iu - ix);

                    // get the distance between the two voxels
                    float distance = sqrt(deltax * deltax + deltay * deltay + deltaz * deltaz);

                    // get the distance to get to this voxel through the current voxel (requires a penalty for visiting this voxel)
                    float distance_through_current = current->distance + distance;
                    float distance_without_current = neighbor_data->distance;

                    if (!neighbor_data->visited) {
                        neighbor_data->prev = current;
                        neighbor_data->distance = distance_through_current;
                        neighbor_data->visited = true;
                        voxel_heap.Insert(dijkstra_index, neighbor_data);
                    }
                    else if (distance_through_current < distance_without_current) {
                        neighbor_data->prev = current;
                        neighbor_data->distance = distance_through_current;
                        voxel_heap.DecreaseKey(dijkstra_index, neighbor_data);
                    }
                }
            }
        }
    }

    std::set<long> refined_skeleton = std::set<long>();

    // iterate over every synapse until it reaches the source
    std::set<long>::iterator it2;
    for (it2 = fixed_points[label].begin(); it2 != fixed_points[label].end(); ++it2) {
        long padded_global_index = *it2;

        long dijkstra_index = dijkstra_map[padded_global_index];
        DijkstraData *data = &(voxel_data[dijkstra_index]);

        // data->prev = NULL for the sources only
        while (data != NULL) {
            // add to the list of skeleton points
            long iv = data->iv;

            if (segments[label][iv] != 4) {
                refined_skeleton.insert(iv);
            }

            data = data->prev;
        }
    }

    // write the skeletons and distances to the output directory
    char skeleton_filename[4096];
    snprintf(skeleton_filename, 4096, "%s/skeletons/%016ld.pts", skeleton_output_directory, label);
    char distance_filename[4096];
    snprintf(distance_filename, 4096, "%s/distances/%016ld.pts", skeleton_output_directory, label);

    // open both files
    FILE *fp = fopen(skeleton_filename, "wb");
    if (!fp) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }
    FILE *distance_fp = fopen(distance_filename, "wb");
    if (!distance_fp) { fprintf(stderr, "Failed to write to %s.\n", distance_filename); exit(-1); }

    WritePtsFileHeader(fp, 1);
    WritePtsFileHeader(distance_fp, 1);

    long num = refined_skeleton.size();

    // write the label and number of voxels
    if (fwrite(&label, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }
    if (fwrite(&num, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }
    if (fwrite(&label, sizeof(long), 1, distance_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", distance_filename); exit(-1); }
    if (fwrite(&num, sizeof(long), 1, distance_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", distance_filename); exit(-1); }

    long *global_indices = new long[num];
    long *local_indices = new long[num];
    float *output_distances = new float[num];

    long checksum = 0;

    // iterate over the refined skeletons
    long iv = 0;
    for (it2 = refined_skeleton.begin(); it2 != refined_skeleton.end(); ++it2, ++iv) {
        long padded_global_index = *it2;

        // get the global index, local index, and distance
        long global_index = GlobalPaddedIndexToIndex(padded_global_index);
        long local_index = GlobalIndexToLocalIndex(global_index);

        long dijkstra_index = dijkstra_map[padded_global_index];
        DijkstraData *dijkstra_data = &(voxel_data[dijkstra_index]);
        float distance = dijkstra_data->distance;

        // update the arrays
        global_indices[iv] = global_index;
        local_indices[iv] = local_index;
        output_distances[iv] = distance;

        // update the checksum
        checksum += (global_indices[iv] + local_indices[iv]);
    }

    // write all of the global and local indices to file
    if (fwrite(&(global_indices[0]), sizeof(long), num, fp) != (unsigned long) num) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }
    if (fwrite(&(local_indices[0]), sizeof(long), num, fp) != (unsigned long) num) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }

    // write the checksum
    if (fwrite(&checksum, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_filename); exit(-1); }

    // write the global indices and widths
    for (long ie = 0; ie < num; ++ie) {
        if (fwrite(&(global_indices[ie]), sizeof(long), 1, distance_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", distance_filename); exit(-1); }
        if (fwrite(&(output_distances[ie]), sizeof(float), 1, distance_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", distance_filename); exit(-1); }
    }

    // close the files
    fclose(fp);
    fclose(distance_fp);

    printf("  Points After Refinement: %ld\n", num);

    // free memory
    delete[] voxel_data;
    delete[] global_indices;
    delete[] local_indices;
    delete[] output_distances;
}



void CppSkeletonRefinement(const char *tmp_directory,
                           const char *synapse_directory,
                           const char *skeleton_output_directory,
                           long label,
                           float input_resolution[3],
                           long input_volume_size[3],
                           long input_block_size[3],
                           long start_indices[3],
                           long nblocks[3])
{
    // update global variables given input values
    for (long iv = 0; iv < NDIMS; ++iv) {
        resolution[iv] = input_resolution[iv];
        volume_size[iv] = input_volume_size[iv];
        block_size[iv] = input_block_size[iv];
        padded_block_size[iv] = block_size[iv] + 2;
        padded_volume_size[iv] = volume_size[iv] + 2;
    }

    // overwrite all global variables from previous calls to this file
    fixed_points = std::map<long, std::set<long> >();
    segments = std::map<long, std::map<long, char> >();

    bool somata_exists = false;

    // iterate through all blocks and read the synapses, skeletons, and somae surfaces
    for (long iz = start_indices[OR_Z]; iz < start_indices[OR_Z] + nblocks[OR_Z]; ++iz) {
        for (long iy = start_indices[OR_Y]; iy < start_indices[OR_Y] + nblocks[OR_Y]; ++iy) {
            for (long ix = start_indices[OR_X]; ix < start_indices[OR_X] + nblocks[OR_X]; ++ix) {
                // read in the somata file if it exists for this label for this block
                // this must occur first so that skeletons and synapses can override the default somata surface value of 4
                char somata_filename[4096];
                snprintf(somata_filename, 4096, "%s/%04ldz-%04ldy-%04ldx/somata_surfaces/%016ld.pts", tmp_directory, iz, iy, ix, label);

                // open the file, if it exists
                FILE *somata_fp = fopen(somata_filename, "rb");
                if (somata_fp) {
                    // read in the points using global coordinates, a mapped value of 3, without populating the fixed point array
                    if (!ReadPtsFile(somata_fp, false, 4, false)) { fprintf(stderr, "Failed to read %s.\n", somata_filename); exit(-1); }

                    // close the file
                    fclose(somata_fp);

                    // a cell body exists for this element
                    somata_exists = true;
                }

                // must read skeletons after somata but before synapses
                char skeleton_filename[4096];
                snprintf(skeleton_filename, 4096, "%s/%04ldz-%04ldy-%04ldx/skeletons/%016ld.pts", tmp_directory, iz, iy, ix, label);

                // open the file, if it exists
                FILE *skeleton_fp = fopen(skeleton_filename, "rb");
                if (skeleton_fp) {
                    // read in the points using global coordinates, a mapped value of 1, without populating the fixed point array
                    if (!ReadPtsFile(skeleton_fp, false, 1, false)) { fprintf(stderr, "Failed to read %s.\n", skeleton_filename); exit(-1); }

                    // close the file
                    fclose(skeleton_fp);
                }

                // must read synapses last to make sure they do not receive a value of 1 (from skeletons) or 4 (from somata surfaces)
                char synapse_filename[4096];
                snprintf(synapse_filename, 4096, "%s/%04ldz-%04ldy-%04ldx.pts", synapse_directory, iz, iy, ix);

                // open the file
                FILE *synapse_fp = fopen(synapse_filename, "rb");
                if (!synapse_fp) { fprintf(stderr, "Failed to read %s.\n", synapse_filename); exit(-1); }

                // read in the points using global coordinates, a mapped value of 3, and populating fixed point array
                if (!ReadPtsFile(synapse_fp, false, 3, true)) { fprintf(stderr, "Failed to read %s.\n", synapse_filename); exit(-1); }

                // close the file
                fclose(synapse_fp);
            }
        }
    }

    // if there are no points for this label, return
    if (not fixed_points[label].size()) return;

    // write temporary files for synapses, skeletons, and somata surfaces for easier visualization
    WriteTempFiles(tmp_directory, label);

    // if not cell body exists, a random synapse becomes the anchor point
    if (not somata_exists) {
        printf("Fixed Points Size: %ld\n", fixed_points[label].size());
        long voxel_index = *(fixed_points[label].begin());
        // segments that are even count as sources
        segments[label][voxel_index] = 2;
    }

    printf("Processing Label: %ld\n", label);
    RunDijkstrasAlgorithm(skeleton_output_directory, label);

    // overwrite all global variables from this iteration
    fixed_points.clear();
    segments.clear();
}
