#include <limits>
#include "cpp-skeletonize.h"



// constant variables

static const int lookup_table_size = 1 << 23;

// lookup tables

static unsigned char *lut_simple;


// global variables

static long somata_downsample_rate = 0;



// constant variables for the directions
// DO NOT CHANGE THIS ORDERING
static const int UP = 0;
static const int DOWN = 1;
static const int NORTH = 2;
static const int SOUTH = 3;
static const int EAST = 4;
static const int WEST = 5;
static const int NTHINNING_DIRECTIONS = 6;



// aggregate variables for all blocks
static std::unordered_set<long> labels_in_block;
static std::unordered_map<long, std::unordered_set<long> > somata_interior_voxels;
static std::unordered_map<long, std::unordered_set<long> > somata_surface_voxels;
static std::unordered_map<long, std::unordered_set<long> > *border_voxels;



// mask variables for bitwise operations
static long long_mask[26];
static unsigned char char_mask[8];
static long n26_offsets[26];
static long n6_offsets[6];



static void set_long_mask(void)
{
    long_mask[ 0] = 0x00000001;
    long_mask[ 1] = 0x00000002;
    long_mask[ 2] = 0x00000004;
    long_mask[ 3] = 0x00000008;
    long_mask[ 4] = 0x00000010;
    long_mask[ 5] = 0x00000020;
    long_mask[ 6] = 0x00000040;
    long_mask[ 7] = 0x00000080;
    long_mask[ 8] = 0x00000100;
    long_mask[ 9] = 0x00000200;
    long_mask[10] = 0x00000400;
    long_mask[11] = 0x00000800;
    long_mask[12] = 0x00001000;
    long_mask[13] = 0x00002000;
    long_mask[14] = 0x00004000;
    long_mask[15] = 0x00008000;
    long_mask[16] = 0x00010000;
    long_mask[17] = 0x00020000;
    long_mask[18] = 0x00040000;
    long_mask[19] = 0x00080000;
    long_mask[20] = 0x00100000;
    long_mask[21] = 0x00200000;
    long_mask[22] = 0x00400000;
    long_mask[23] = 0x00800000;
    long_mask[24] = 0x01000000;
    long_mask[25] = 0x02000000;
}



static void set_char_mask(void)
{
    char_mask[0] = 0x01;
    char_mask[1] = 0x02;
    char_mask[2] = 0x04;
    char_mask[3] = 0x08;
    char_mask[4] = 0x10;
    char_mask[5] = 0x20;
    char_mask[6] = 0x40;
    char_mask[7] = 0x80;
}



static void PopulateOffsets(void)
{
    n26_offsets[0] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X] - 1;
    n26_offsets[1] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X];
    n26_offsets[2] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X] + 1;
    n26_offsets[3] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] - 1;
    n26_offsets[4] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X];
    n26_offsets[5] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] + 1;
    n26_offsets[6] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X] - 1;
    n26_offsets[7] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X];
    n26_offsets[8] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X] + 1;

    n26_offsets[9] = -1 * padded_block_size[OR_X] - 1;
    n26_offsets[10] = -1 * padded_block_size[OR_X];
    n26_offsets[11] = -1 * padded_block_size[OR_X] + 1;
    n26_offsets[12] = -1;
    n26_offsets[13] = +1;
    n26_offsets[14] = padded_block_size[OR_X] - 1;
    n26_offsets[15] = padded_block_size[OR_X];
    n26_offsets[16] = padded_block_size[OR_X] + 1;

    n26_offsets[17] = padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X] - 1;
    n26_offsets[18] = padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X];
    n26_offsets[19] = padded_block_size[OR_Y] * padded_block_size[OR_X] - padded_block_size[OR_X] + 1;
    n26_offsets[20] = padded_block_size[OR_Y] * padded_block_size[OR_X] - 1;
    n26_offsets[21] = padded_block_size[OR_Y] * padded_block_size[OR_X];
    n26_offsets[22] = padded_block_size[OR_Y] * padded_block_size[OR_X] + 1;
    n26_offsets[23] = padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X] - 1;
    n26_offsets[24] = padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X];
    n26_offsets[25] = padded_block_size[OR_Y] * padded_block_size[OR_X] + padded_block_size[OR_X] + 1;

    // use this order to go UP, DOWN, NORTH, SOUTH, EAST, WEST
    // DO NOT CHANGE THIS ORDERING
    n6_offsets[0] = -1 * padded_block_size[OR_X];                                   // negative y direction
    n6_offsets[1] = padded_block_size[OR_X];                                        // positive y direction
    n6_offsets[2] = -1 * padded_block_size[OR_Y] * padded_block_size[OR_X];         // negative z direction
    n6_offsets[3] = padded_block_size[OR_Y] * padded_block_size[OR_X];              // positive z direction
    n6_offsets[4] = +1;                                                             // positive x direction
    n6_offsets[5] = -1;                                                             // negative x direction
}



// very simple double linked list data structure
typedef struct {
      long iv, iz, iy, ix;
      void *next;
      void *prev;
} ListElement;



typedef struct {
    void *first;
    void *last;
} List;



typedef struct {
    long iv, iz, iy, ix;
} Voxel;



typedef struct {
    Voxel v;
    ListElement *ptr;
    void *next;
} Cell;



typedef struct {
    Cell *head;
    Cell *tail;
    long length;
} PointList;



// variables for each processed block
long current_label;
static std::unordered_map<long, float> widths;
static List surface_voxels;



static void NewSurfaceVoxel(long iv, long iz, long iy, long ix, List &surface_voxels)
{
    ListElement *LE = new ListElement();
    LE->iv = iv;
    LE->iz = iz;
    LE->iy = iy;
    LE->ix = ix;

    LE->next = NULL;
    LE->prev = surface_voxels.last;

    if (surface_voxels.last != NULL) ((ListElement *) surface_voxels.last)->next = LE;
    surface_voxels.last = LE;
    if (surface_voxels.first == NULL) surface_voxels.first = LE;
}



static void RemoveSurfaceVoxel(ListElement *LE, List &surface_voxels)
{
    ListElement *LE2;
    if (surface_voxels.first == LE) surface_voxels.first = LE->next;
    if (surface_voxels.last == LE) surface_voxels.last = LE->prev;

    if (LE->next != NULL) {
        LE2 = (ListElement *)(LE->next);
        LE2->prev = LE->prev;
    }
    if (LE->prev != NULL) {
        LE2 = (ListElement *)(LE->prev);
        LE2->next = LE->next;
    }

    delete LE;
}



static void CreatePointList(PointList *s)
{
    s->head = NULL;
    s->tail = NULL;
    s->length = 0;
}



static void AddToList(PointList *s, Voxel e, ListElement *ptr)
{
    Cell *newcell = new Cell();
    newcell->v = e;
    newcell->ptr = ptr;
    newcell->next = NULL;

    if (s->head == NULL) {
        s->head = newcell;
        s->tail = newcell;
        s->length = 1;
    }
    else {
        s->tail->next = newcell;
        s->tail = newcell;
        s->length++;
    }
}



static Voxel GetFromList(PointList *s, ListElement **ptr)
{
    Voxel V;
    Cell *tmp;

    V.iv = -1;
    V.ix = -1;
    V.iy = -1;
    V.iz = -1;
    (*ptr) = NULL;

    if (s->length == 0) return V;
    else {
        V = s->head->v;
        (*ptr) = s->head->ptr;
        tmp = (Cell *) s->head->next;
        delete s->head;
        s->head = tmp;
        s->length--;
        if (s->length == 0) {
            s->head = NULL;
            s->tail = NULL;
        }
        return V;
    }
}



static void DestroyPointList(PointList *s)
{
    ListElement *ptr;
    while (s->length) GetFromList(s, &ptr);
}



static void InitializeLookupTables(const char *lookup_table_directory)
{
    // read the simple lookup table
    char lut_filename[4096];
    snprintf(lut_filename, 4096, "%s/lut_simple.dat", lookup_table_directory);

    // open the lookup table
    FILE *lut_file = fopen(lut_filename, "rb");
    if (!lut_file) { fprintf(stderr, "Failed to read %s\n", lut_filename); exit(-1); }

    // read the lookup table into an array
    lut_simple = new unsigned char[lookup_table_size];

    if (fread(lut_simple, 1, lookup_table_size, lut_file) != lookup_table_size) { fprintf(stderr, "Failed to read %s\n", lut_filename); exit(-1); }

    // close file
    fclose(lut_file);

    // set the mask variables
    set_char_mask();
    set_long_mask();
}



static bool Simple26_6(unsigned int neighbors)
{
    return lut_simple[(neighbors >> 3)] & char_mask[neighbors % 8];
}


static void PopulateSomata(long *somata)
{
    // save characteristics of the downsampled volume, which are only needed and therfore defined within this function
    const long DSP = somata_downsample_rate;

    // get the block size and padded block size for the somata data sets
    long somata_block_size[3] = {
        block_size[OR_Z] / DSP,
        block_size[OR_Y] / DSP,
        block_size[OR_X] / DSP,
    };
    long padded_somata_block_size[3];
    for (long iv = 0; iv < NDIMS; ++iv) {
        padded_somata_block_size[iv] = somata_block_size[iv] + 2;
    }

    // keep track of the labels in the volume
    std::vector<long> somata_labels = std::vector<long>();

    // number of voxels in the downsampled data
    long nentries = somata_block_size[OR_Z] * somata_block_size[OR_Y] * somata_block_size[OR_X];

    for (long down_index = 0; down_index < nentries; down_index++){
        // get the label at this location in the dataset
        long label = somata[down_index];

        // skip background voxels
        if (not label) continue;

        // create new sets of voxels for both the interior and surface
        if (somata_interior_voxels.find(label) == somata_interior_voxels.end()) {
            somata_interior_voxels[label] = std::unordered_set<long>();
            somata_surface_voxels[label] = std::unordered_set<long>();
            somata_labels.push_back(label);
        }

        // get the offsets when downsampled
        long n6_offsets_downsampled[6];
        n6_offsets_downsampled[0] = -1 * padded_somata_block_size[OR_X]; // negative y direction
        n6_offsets_downsampled[1] = padded_somata_block_size[OR_X]; // positive y direction
        n6_offsets_downsampled[2] = -1 * padded_somata_block_size[OR_Y] * padded_somata_block_size[OR_X]; // negative z direction
        n6_offsets_downsampled[3] = padded_somata_block_size[OR_Y] * padded_somata_block_size[OR_X]; // positive z direction
        n6_offsets_downsampled[4] = +1; // positive x direction
        n6_offsets_downsampled[5] = -1; // negative x direction

        // keep track of the somata voxels that belong to the surface
        bool z_positive_surface = false;
        bool y_positive_surface = false;
        bool x_positive_surface = false;
        bool z_negative_surface = false;
        bool y_negative_surface = false;
        bool x_negative_surface = false;

        // get the padded index and iterate over all six neighbors
        long padded_down_index = GenericIndexToPaddedIndex(down_index, somata_block_size);

        // get downsampled coordinates
        long down_iz, down_iy, down_ix;
        GenericIndexToIndices(down_index, down_iz, down_iy, down_ix, somata_block_size);

        // get the upsampled coordinates from the downsampled coordinates
        long iz = down_iz * DSP;
        long iy = down_iy * DSP;
        long ix = down_ix * DSP;

        for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
            long padded_neighbor_index = padded_down_index + n6_offsets_downsampled[dir];

            // skip the boundary elements
            long ik, ij, ii;
            GenericIndexToIndices(padded_neighbor_index, ik, ij, ii, padded_somata_block_size);
            if (ik == 0 or ik == padded_somata_block_size[OR_Z] - 1) continue;
            if (ij == 0 or ij == padded_somata_block_size[OR_Y] - 1) continue;
            if (ii == 0 or ii == padded_somata_block_size[OR_X] - 1) continue;

            long neighbor_index = GenericPaddedIndexToIndex(padded_neighbor_index, somata_block_size);

            if (somata[neighbor_index] != label) {
                if (dir == 0) y_negative_surface = true;
                if (dir == 1) y_positive_surface = true;
                if (dir == 2) z_negative_surface = true;
                if (dir == 3) z_positive_surface = true;
                if (dir == 4) x_positive_surface = true;
                if (dir == 5) x_negative_surface = true;
            }
        }

        // iterate through all points in the upsampled region of size (DSP * DSP * DSP)
        for (long iw = iz; iw < iz + DSP; ++iw) {
            for (long iv = iy; iv < iy + DSP; ++iv) {
                for (long iu = ix; iu < ix + DSP; ++iu) {
                    long index = LocalIndicesToIndex(iw, iv, iu);
                    long padded_index = LocalIndexToPaddedIndex(index);

                    // add if this belongs to the surface
                    if (z_negative_surface and iw == iz) somata_surface_voxels[label].insert(padded_index);
                    else if (y_negative_surface and iv == iy) somata_surface_voxels[label].insert(padded_index);
                    else if (x_negative_surface and iu == ix) somata_surface_voxels[label].insert(padded_index);
                    else if (z_positive_surface and iw == iz + DSP - 1) somata_surface_voxels[label].insert(padded_index);
                    else if (y_positive_surface and iv == iy + DSP - 1) somata_surface_voxels[label].insert(padded_index);
                    else if (x_positive_surface and iu == ix + DSP - 1) somata_surface_voxels[label].insert(padded_index);
                    else somata_interior_voxels[label].insert(padded_index);
                }
            }
        }
    }
}



static void PopulateSegments(long *segmentation)
{
    long nentries = block_size[OR_Z] * block_size[OR_Y] * block_size[OR_X];

    // add each voxel to an unordered mapping of voxels
    for (long index = 0; index < nentries; ++index) {
        long label = segmentation[index];

        // skip background elements
        if (not label) continue;

        // get the padded local index
        long padded_index = LocalIndexToPaddedIndex(index);

        // create a new unordered map for this label
        if (segments.find(label) == segments.end()) {
            segments[label] = std::unordered_map<long, char>();
            fixed_points[label] = std::unordered_set<long>();
            for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
                border_voxels[dir][label] = std::unordered_set<long>();
            }
            labels_in_block.insert(label);
        }

        // skip over points inside the cell body
        if (somata_interior_voxels[label].find(padded_index) == somata_interior_voxels[label].end()) {
            // add this point to the segments list as interior (surface voxels found later)
            segments[label][padded_index] = 1;
        }

        // add points to the list of voxels on the wall
        long iz, iy, ix;
        LocalIndexToIndices(index, iz, iy, ix);

        // add the borderpoints if it is on the wall but not on the edge or corner
        if (iz == block_size[OR_Z] - 1) {
            if (not (iy == 0 or iy == block_size[OR_Y] - 1 or ix == 0 or ix == block_size[OR_X] - 1)) border_voxels[SOUTH][label].insert(padded_index);
        }
        if (iy == block_size[OR_Y] - 1) {
            if (not (iz == 0 or iz == block_size[OR_Z] - 1 or ix == 0 or ix == block_size[OR_X] - 1)) border_voxels[DOWN][label].insert(padded_index);
        }
        if (ix == block_size[OR_X] - 1) {
            if (not (iz == 0 or iz == block_size[OR_Z] - 1 or iy == 0 or iy == block_size[OR_Y] - 1)) border_voxels[EAST][label].insert(padded_index);
        }
        if (iz == 0) {
            if (not (iy == 0 or iy == block_size[OR_Y] - 1 or ix == 0 or ix == block_size[OR_X] - 1)) border_voxels[NORTH][label].insert(padded_index);
        }
        if (iy == 0) {
            if (not (iz == 0 or iz == block_size[OR_Z] - 1 or ix == 0 or ix == block_size[OR_X] - 1)) border_voxels[UP][label].insert(padded_index);
        }
        if (ix == 0) {
            if (not (iz == 0 or iz == block_size[OR_Z] - 1 or iy == 0 or iy == block_size[OR_Y] - 1)) border_voxels[WEST][label].insert(padded_index);
        }
    }

    // points on the surface of the cell body get a value of 4 (do not remove)
    std::unordered_map<long, std::unordered_set<long> >::iterator label_iterator;
    for (label_iterator = somata_surface_voxels.begin(); label_iterator != somata_surface_voxels.end(); ++label_iterator) {
        long label = label_iterator->first;

        // iterate over all voxels in the surface of this somata
        std::unordered_set<long>::iterator voxel_iterator;
        for (voxel_iterator = somata_surface_voxels[label].begin(); voxel_iterator != somata_surface_voxels[label].end(); ++voxel_iterator) {
            long padded_index = *voxel_iterator;
            segments[label][padded_index] = 4;
        }
    }
}



static void ReadSynapses(const char *synapse_directory, long current_block_index[3])
{
    char synapse_filename[4096];
    snprintf(synapse_filename, 4096, "%s/%04ldz-%04ldy-%04ldx.pts", synapse_directory, current_block_index[OR_Z], current_block_index[OR_Y], current_block_index[OR_X]);

    // open the file
    FILE *fp = fopen(synapse_filename, "rb");
    if (!fp) { fprintf(stderr, "Failed to read %s.\n", synapse_filename); exit(-1); }

    // read in the points using local coordinates, a mapped value of 3, and populating fixed point array
    if (!ReadPtsFile(fp, true, 3, true)) { fprintf(stderr, "Failed to read %s.\n", synapse_filename); exit(-1); }

    // close the file
    fclose(fp);
}



static void ReadAnchorPoints(const char *tmp_directory)
{
    const char *directions[NTHINNING_DIRECTIONS] = {
        "x-min",
        "x-max",
        "y-min",
        "y-max",
        "z-min",
        "z-max"
    };

    // consider all six directions
    for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
        char anchor_pts_filename[4096];
        snprintf(anchor_pts_filename, 4096, "%s/%s-computed-anchor-points.pts", tmp_directory, directions[dir]);

        // skip anchor point files that do not exist
        FILE *fp = fopen(anchor_pts_filename, "rb");
        if (!fp) continue;

        // read in the points using local coordinates, a mapped value of 3, and populating fixed point array
        if (!ReadPtsFile(fp, true, 3, true)) { fprintf(stderr, "Failed to read %s.\n", anchor_pts_filename); exit(-1); }

        // close the file
        fclose(fp);
    }
}




static void CollectSurfaceVoxels(void)
{
    long n_surface_voxels = 0;

    // go through all voxels and check their six neighbors
    std::unordered_map<long, char>::iterator it;
    for (it = segments[current_label].begin(); it != segments[current_label].end(); ++it) {
        // all of these elements are either 1, 3, or 4 and in the segment
        long index = it->first;

        // initialize widths to maximum float value
        widths[index] = std::numeric_limits<float>::max();

        long iz, iy, ix;
        LocalPaddedIndexToPaddedIndices(index, iz, iy, ix);

        // check the 6 neighbors
        for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
            long neighbor_index = index + n6_offsets[dir];

            long ik, ij, ii;
            LocalPaddedIndexToPaddedIndices(neighbor_index, ik, ij, ii);

            // skip the fake boundary elements
            if ((ik == 0) or (ik == padded_block_size[OR_Z] - 1)) continue;
            if ((ij == 0) or (ij == padded_block_size[OR_Y] - 1)) continue;
            if ((ii == 0) or (ii == padded_block_size[OR_X] - 1)) continue;

            if (segments[current_label].find(neighbor_index) == segments[current_label].end()) {
                // this location is a boundary so create a surface voxel and break
                // cannot update it->second if it is synapse so need this test!!
                if (it->second == 1) {
                    it->second = 2;
                    NewSurfaceVoxel(index, iz, iy, ix, surface_voxels);
                    n_surface_voxels ++;
                }

                // any of these voxels can have width zero since we already verify that
                // the non-label neighbor is not outside the standard volume size
                widths[index] = 0;

                break;
            }
        }
    }

    printf("  Initial Surface Voxels: %ld\n", n_surface_voxels);
}



unsigned int Collect26Neighbors(long iz, long iy, long ix)
{
    unsigned int neighbors = 0;

    long index = LocalPaddedIndicesToPaddedIndex(iz, iy, ix);

    // some of these lookups will create a new entry but the region is
    // shrinking so memory overhead is minimal
    for (long iv = 0; iv < 26; ++iv) {
        if (segments[current_label][index + n26_offsets[iv]]) neighbors |= long_mask[iv];
    }

    return neighbors;
}



void DetectSimpleBorderPoints(PointList *deletable_points, int direction)
{
    ListElement *LE = (ListElement *)surface_voxels.first;
    while (LE != NULL) {
        long iv = LE->iv;
        long ix = LE->ix;
        long iy = LE->iy;
        long iz = LE->iz;

        // not a synapse endpoint (need this here since endpoints are on the list of surfaces)
        // this will only be called on things on the surface already so already in unordered_map
        if (segments[current_label][iv] == 2) {
            long value = 0;

            // is the neighbor in the corresponding direction not in the segment
            // some of these keys will not exist but will default to 0 value
            // the search region retracts in from the boundary so limited memory overhead
            // the n6_offsets are in the order UP, DOWN, NORTH, SOUTH, EAST, WEST
            value = segments[current_label][iv + n6_offsets[direction]];

            // see if the required point belongs to a different segment
            if (!value) {
                unsigned int neighbors = Collect26Neighbors(iz, iy, ix);

                // deletable point
                if (Simple26_6(neighbors)) {
                    Voxel voxel;

                    voxel.iv = iv;
                    voxel.iz = iz;
                    voxel.iy = iy;
                    voxel.ix = ix;

                    AddToList(deletable_points, voxel, LE);
                }
            }
        }
        LE = (ListElement *) LE->next;
    }
}



static long ThinningIterationStep(void)
{
    // keep track of the number of changed voxels
    long changed = 0;

    // iterate through every direction
    for (int direction = 0; direction < NTHINNING_DIRECTIONS; ++direction) {
        PointList deletable_points;
        ListElement *ptr;

        CreatePointList(&deletable_points);

        DetectSimpleBorderPoints(&deletable_points, direction);

        while (deletable_points.length) {
            Voxel voxel = GetFromList(&deletable_points, &ptr);

            long index = voxel.iv;
            long iz = voxel.iz;
            long iy = voxel.iy;
            long ix = voxel.ix;

            // do not remove voxel in the dirction of the outer facing surface
            // the directions of border voxels are reverse of the direction of erosion
            // e.g., if you are thinning from UP (-y direction), do not remove elements on the DOWN wall (y max)
            if (border_voxels[DOWN][current_label].find(index) != border_voxels[DOWN][current_label].end() && direction == UP) continue;
            if (border_voxels[UP][current_label].find(index) != border_voxels[UP][current_label].end() && direction == DOWN) continue;
            if (border_voxels[SOUTH][current_label].find(index) != border_voxels[SOUTH][current_label].end() && direction == NORTH) continue;
            if (border_voxels[NORTH][current_label].find(index) != border_voxels[NORTH][current_label].end() && direction == SOUTH) continue;
            if (border_voxels[WEST][current_label].find(index) != border_voxels[WEST][current_label].end() && direction == EAST) continue;
            if (border_voxels[EAST][current_label].find(index) != border_voxels[EAST][current_label].end() && direction == WEST) continue;

            // check if simple, if so, delete it
            unsigned int neighbors = Collect26Neighbors(iz, iy, ix);

            if (Simple26_6(neighbors)) {
                // delete the simple point
                segments[current_label][index] = 0;

                // add the new surface voxels
                for (long ip = 0; ip < NTHINNING_DIRECTIONS; ++ip) {
                    long neighbor_index = index + n6_offsets[ip];

                    // previously not on the surface but is in the object
                    // widths of voxels start at maximum and first updated when put on surface
                    if (segments[current_label][neighbor_index] == 1) {
                        long iw, iv, iu;
                        LocalPaddedIndexToPaddedIndices(neighbor_index, iw, iv, iu);
                        NewSurfaceVoxel(neighbor_index, iw, iv, iu, surface_voxels);

                        // convert to a surface point
                        segments[current_label][neighbor_index] = 2;
                    }
                }

                // check all 26 neighbors to see if width is better going through this voxel
                for (long ip = 0; ip < 26; ++ip) {
                    long neighbor_index = index + n26_offsets[ip];

                    // skip background voxels (those that do not belong to this label)
                    if (!segments[current_label][neighbor_index]) continue;

                    // get this index in (x, y, z)
                    long iw, iv, iu;
                    LocalPaddedIndexToPaddedIndices(neighbor_index, iw, iv, iu);

                    // get the distance from the voxel to be deleted
                    float diffz = resolution[OR_Z] * (iz - iw);
                    float diffy = resolution[OR_Y] * (iy - iv);
                    float diffx = resolution[OR_X] * (ix - iu);

                    float distance = sqrt(diffx * diffx + diffy * diffy + diffz * diffz);
                    float current_width = widths[neighbor_index];

                    if (widths[index] + distance < current_width) {
                        widths[neighbor_index] = widths[index] + distance;
                    }
                }

                // remove this from the surface voxels
                RemoveSurfaceVoxel(ptr, surface_voxels);

                changed += 1;
            }
        }

        // delete this list of points for this direction
        DestroyPointList(&deletable_points);
    }

    // return the number of changes
    return changed;
}



static void SequentialThinning(void)
{
    // create a vector of surface voxels
    CollectSurfaceVoxels();

    int iteration = 0;
    long changed = 0;

    do {
        changed = ThinningIterationStep();
        iteration++;

        printf("  Iteration %d: %ld points removed\n", iteration, changed);
    } while (changed);
}



static void WriteSkeletonOutputFiles(const char *tmp_directory, long current_block_index[3])
{
    char skeleton_output_filename[4096];
    snprintf(skeleton_output_filename, 4096, "%s/skeletons/%016ld.pts", tmp_directory, current_label);
    char width_output_filename[4096];
    snprintf(width_output_filename, 4096, "%s/widths/%016ld.pts", tmp_directory, current_label);

    FILE *fp = fopen(skeleton_output_filename, "wb");
    if (!fp) { fprintf(stderr, "Failed to write %s.\n", skeleton_output_filename); exit(-1); }
    FILE *width_fp = fopen(width_output_filename, "wb");
    if (!width_fp) { fprintf(stderr, "Failed to write %s.\n", width_output_filename); exit(-1); }

    WritePtsFileHeader(fp, 1);
    WritePtsFileHeader(width_fp, 1);

    // count the number of remaining points
    long num = 0;
    ListElement *LE = (ListElement *) surface_voxels.first;
    while (LE != NULL) {
        num++;
        LE = (ListElement *)LE->next;
    }

    num += fixed_points[current_label].size();

    printf("    Remaining Voxels: %ld\n", num);

    // write the label and number of voxels
    if (fwrite(&current_label, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_output_filename); exit(-1); }
    if (fwrite(&num, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_output_filename); exit(-1); }
    if (fwrite(&current_label, sizeof(long), 1, width_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", width_output_filename); exit(-1); }
    if (fwrite(&num, sizeof(long), 1, width_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", width_output_filename); exit(-1); }

    long *global_indices = new long[num];
    long *local_indices = new long[num];
    float *output_widths = new float[num];

    long checksum = 0;
    long iv = 0;

    // write surface voxels (global index)
    while (surface_voxels.first != NULL) {
        // get the surface voxels
        ListElement *LE = (ListElement *) surface_voxels.first;

        // get the padded index and width
        long padded_index = LE->iv;
        output_widths[iv] = widths[padded_index];

        // get the local and global indices
        long local_index = LocalPaddedIndexToIndex(padded_index);
        long iz, iy, ix;
        LocalIndexToIndices(local_index, iz, iy, ix);

        long global_index = LocalIndicesToGlobalIndex(iz, iy, ix, current_block_index);

        global_indices[iv] = global_index;
        local_indices[iv] = local_index;

        // update the checksum
        checksum += (global_indices[iv] + local_indices[iv]);

        // remove this voxel
        RemoveSurfaceVoxel(LE, surface_voxels);

        // increment counter
        ++iv;
    }

    // add in the fixed points
    std::unordered_set<long>::iterator it;
    for (it = fixed_points[current_label].begin(); it != fixed_points[current_label].end(); ++it, ++iv) {
        // get the padded index
        long padded_index = *it;

        // get the local and global indices
        long local_index = LocalPaddedIndexToIndex(padded_index);
        long iz, iy, ix;
        LocalIndexToIndices(local_index, iz, iy, ix);

        long global_index = LocalIndicesToGlobalIndex(iz, iy, ix, current_block_index);

        global_indices[iv] = global_index;
        local_indices[iv] = local_index;
        output_widths[iv] = widths[padded_index];

        // update the checksum
        checksum += (global_indices[iv] + local_indices[iv]);
    }

    // write all of the global and local indices to file
    if (fwrite(&(global_indices[0]), sizeof(long), num, fp) != (unsigned long) num) { fprintf(stderr, "Failed to write to %s.\n", skeleton_output_filename); exit(-1); }
    if (fwrite(&(local_indices[0]), sizeof(long), num, fp) != (unsigned long) num) { fprintf(stderr, "Failed to write to %s.\n", skeleton_output_filename); exit(-1); }

    // write the checksum
    if (fwrite(&checksum, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", skeleton_output_filename); exit(-1); }

    // write the global indices and widths
    for (long ie = 0; ie < num; ++ie) {
        if (fwrite(&(global_indices[ie]), sizeof(long), 1, width_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", width_output_filename); exit(-1); }
        if (fwrite(&(output_widths[ie]), sizeof(float), 1, width_fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", width_output_filename); exit(-1); }
    }

    // close file
    fclose (fp);
    fclose (width_fp);

    // free memory
    delete[] global_indices;
    delete[] local_indices;
    delete[] output_widths;
}



static void WriteSomataSurfaces(const char *tmp_directory, long current_block_index[3])
{
    // iterate over all labels in the map
    std::unordered_map<long, std::unordered_set<long> >::iterator it;
    for (it = somata_surface_voxels.begin(); it != somata_surface_voxels.end(); ++it) {
        long label = it->first;

        // get filename for this cell body
        char somata_filename[4096];
        snprintf(somata_filename, 4096, "%s/somata_surfaces/%016ld.pts", tmp_directory, label);

        // open file
        FILE *fp = fopen(somata_filename, "wb");
        if (!fp) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }

        // write the header (one label per file)
        WritePtsFileHeader(fp, 1);

        // go through all voxels in the set and add to local and global arrays
        std::unordered_set<long> voxels = it->second;
        unsigned long nvoxels = voxels.size();

        // write the label and the number of voxels
        if (fwrite(&label, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }
        if (fwrite(&nvoxels, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }

        long *local_indices = new long[nvoxels];
        long *global_indices = new long[nvoxels];

        // keep a checksum to verify input and output
        long checksum = 0;

        // go through every voxel (currently they are padded)
        long iv = 0; // counter for the number of voxels processed
        for (std::unordered_set<long>::iterator it = voxels.begin(); it != voxels.end(); ++it, ++iv) {
            long padded_index = *it;

            local_indices[iv] = LocalPaddedIndexToIndex(padded_index);

            // convert the local index into indicies
            long iz, iy, ix;
            LocalIndexToIndices(local_indices[iv], iz, iy, ix);

            global_indices[iv] = LocalIndicesToGlobalIndex(iz, iy, ix, current_block_index);

            checksum += (local_indices[iv] + global_indices[iv]);
        }

        // write the global indices, local indices, and checksum
        if (fwrite(&(global_indices[0]), sizeof(long), nvoxels, fp) != nvoxels) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }
        if (fwrite(&(local_indices[0]), sizeof(long), nvoxels, fp) != nvoxels) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }
        if (fwrite(&checksum, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to write to %s.\n", somata_filename); exit(-1); }

        // free memory
        delete[] local_indices;
        delete[] global_indices;

        // close file
        fclose(fp);
    }
}



void CppTopologicalThinning(const char *lookup_table_directory,
    const char *tmp_directory,
    const char *synapse_directory,
    long *segmentation,
    long *somata,
    long input_somata_downsample_rate,
    float input_resolution[3],
    long input_volume_size[3],
    long input_block_size[3],
    long current_block_index[3])
{
    // update global variables given input values
    for (long iv = 0; iv < NDIMS; ++iv) {
        resolution[iv] = input_resolution[iv];
        volume_size[iv] = input_volume_size[iv];
        block_size[iv] = input_block_size[iv];
        padded_block_size[iv] = block_size[iv] + 2;
        padded_volume_size[iv] = volume_size[iv] + 2;
    }
    somata_downsample_rate = input_somata_downsample_rate;

    // overwrite all global variables from previous calls to this file
    labels_in_block = std::unordered_set<long>();
    fixed_points = std::unordered_map<long, std::unordered_set<long> >();
    somata_interior_voxels = std::unordered_map<long, std::unordered_set<long> >();
    somata_surface_voxels = std::unordered_map<long, std::unordered_set<long> >();
    segments = std::unordered_map<long, std::unordered_map<long, char> >();

    // create mappings for every wall
    border_voxels = new std::unordered_map<long, std::unordered_set<long> >[NTHINNING_DIRECTIONS];
    for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
        border_voxels[dir] = std::unordered_map<long, std::unordered_set<long> >();
    }

    // create the mappings for somata and for segmentations
    // somata should go first so to not add points from the soma to the segmentation
    // only populate the somata if a somata path exists
    if (somata_downsample_rate) PopulateSomata(somata);
    PopulateSegments(segmentation);

    // read in the synapses and the anchor points
    ReadSynapses(synapse_directory, current_block_index);

    // read in the anchor points
    ReadAnchorPoints(tmp_directory);

    // populate the offsets for easier linear access
    PopulateOffsets();

    // initialize the lookup table
    InitializeLookupTables(lookup_table_directory);

    // iterate over all labels in the volume for thinning
    std::unordered_set<long>::iterator it;
    for (it = labels_in_block.begin(); it != labels_in_block.end(); ++it) {
        // initialize new widths mapping for this label
        widths = std::unordered_map<long, float>();

        current_label = *it;

        printf("Processing Neuron %ld\n", current_label);

        // thin the volume
        SequentialThinning();

        // write the values to output
        WriteSkeletonOutputFiles(tmp_directory, current_block_index);

        // clear widths mapping
        widths.clear();
    }

    // write the somata surfaces to file
    WriteSomataSurfaces(tmp_directory, current_block_index);

    // overwrite all global variables from this iteration
    labels_in_block.clear();
    fixed_points.clear();
    somata_interior_voxels.clear();
    somata_surface_voxels.clear();
    segments.clear();

    for (long dir = 0; dir < NTHINNING_DIRECTIONS; ++dir) {
        border_voxels[dir].clear();
    }

    // free memory
    delete[] lut_simple;
    delete[] border_voxels;
}
