#ifndef __CPP_PGM_IMAGE__
#define __CPP_PGM_IMAGE__


#include <vector>



class PGMImage {
    public:
        unsigned char* data;
        int width, height, depth;
        PGMImage( int width, int height, int depth );
        ~PGMImage();
        void createBorder( int bwidth, unsigned char color = 0 );
};



void ThinImage(const char *lookup_table_directory, PGMImage* img, std::vector<long> &iu_centers, std::vector<long> &iv_centers);

#endif
