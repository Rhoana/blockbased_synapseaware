#include <stdio.h>
#include <stdlib.h>
#include <queue>
#include "PGMImage.h"




#define CONTOUR_MASK 3
#define OBJECT 1



using namespace std;




PGMImage::PGMImage( int width, int height, int depth )
{
    this->width = width;
    this->height = height;
    this->depth = depth;

    this->data = NULL;
    this->data = ( unsigned char* ) malloc ( width * height * sizeof( unsigned char ) );

    if ( this->data == NULL ) {
        fprintf(stderr, "PGMImage: Allocation error. Not enough memory. \n"); exit(-1);;

        return;
    }

    int size = width * height;

    for ( int i = 0; i < size; i++ ) {
        this->data[ i ] = 0;
    }
}



PGMImage::~PGMImage()
{
    delete[] this->data;
}



void PGMImage::createBorder( int bwidth, unsigned char color )
{

    if ( this->data == NULL ) {
        fprintf(stderr, "ERROR: PGMImage::createBorder: data does not exist\n "); exit(-1);;
    }

    int new_width, new_height;
    new_width = this->width + 2 * bwidth;
    new_height = this->height + 2 * bwidth;

    unsigned long new_length = new_width * new_height;
    unsigned char *temp;
    temp = ( unsigned char* ) malloc ( new_length * sizeof( unsigned char ) );

    if ( !temp ) {
        fprintf(stderr, "ERROR: PGMImage::createBorder: not enough memory for temp array\n "); exit(-1);;
    }

    unsigned long orig_index, new_index;

    for ( unsigned long i = 0; i < new_length; i++ ) temp[ i ] = color;

    if ( bwidth > 0 ) {
        for ( int y = 0; y < height; y++ ) {
            for ( int x = 0; x < width; x++ ) {
                orig_index = y * width + x;
                new_index = ( y + bwidth ) * (width + 2*bwidth ) + (x + bwidth);
                temp[ new_index ] = this->data[orig_index];
            }
        }
    } else {
        for ( int y = -bwidth; y < height + bwidth; y++ ) {
            for ( int x = -bwidth; x < width + bwidth; x++ ) {
                orig_index = y * width + x;
                new_index = ( y + bwidth ) * (width + 2*bwidth ) + (x + bwidth);
                temp[ new_index ] = this->data[orig_index];
            }
        }
    }

    free ( data );
    data = temp;
    this->width += 2*bwidth;
    this->height += 2 * bwidth;
}



// iteration step
unsigned long palagyi_fpta( PGMImage* img, queue<unsigned long> &contour, unsigned char* lut )
{
    unsigned long length = contour.size();

    int w = img->width;

    int env[24] = { -w-1, -w, -w+1, 1, w+1, w, w-1,-1, -2, -w-2, -2*w-2, -2*w-1, -2*w, -2*w+1, -2*w+2, -w+2, 2, w+2, 2*w+2, 2*w+1, 2*w, 2*w-1, 2*w-2, w-2 };
    int n4[4] = { -w, 1, w, -1 };

    queue<unsigned long> deletable;

    for ( unsigned long t = 0; t < length; t++ ) {
        unsigned long p = contour.front();
        contour.pop();
        unsigned long code = 0;
        if ( img->data[p] == CONTOUR_MASK ) {
            for ( unsigned long i = 0, k = 1; i < 24; i++, k*=2 ) {
                if ( img->data[p+env[i]] != 0 ) {
                    code |= k;
                }
            }
            int endpoint = 0;

            if ( endpoint == 0 ) {
                if ( lut[code] == 1 ) deletable.push(p); else contour.push(p);
            }
        }
    }

    length = deletable.size();

    for ( unsigned long i = 0; i < length; i++ ) {
        unsigned long p = deletable.front();
        deletable.pop();

        img->data[p] = 0;
        for ( int j = 0; j < 4; j++ ) {
            if ( img->data[p+n4[j]] == OBJECT ) {
                img->data[p+n4[j]] = CONTOUR_MASK;
                contour.push( p+n4[j] );
            }
        }
    }

    return length;
}



void fpta_thinning( PGMImage* img, unsigned char *lut, unsigned char *lut2 )
{
    queue<unsigned long> contour;
    int w = img->width, h = img->height;
    unsigned long size = w * h;
    int n4[4] = { -w, 1, w, -1 };

    for ( unsigned long i = 0; i < size; i++ ) {
        if ( img->data[i] == OBJECT ) {
            for ( int j = 0; j < 4; j++ ) {
                if ( img->data[i+n4[j]] == 0 ) {
                    contour.push( i );
                    img->data[i] = CONTOUR_MASK;
                }
            }
        }
    }

    int iter = 0;
    unsigned long deleted = 0;

    do {
        deleted = palagyi_fpta( img, contour, lut );

        iter++;
    } while ( deleted > 0 );
}



void ThinImage(const char *lookup_table_directory, PGMImage* img, std::vector<long> &iu_centers, std::vector<long> &iv_centers)
{
    FILE* fp = NULL;

    char lookup_table_filename[4096];
    snprintf(lookup_table_filename, 4096, "%s/ronse_fpta.lut", lookup_table_directory);
    fp = fopen( lookup_table_filename, "rb" );

    unsigned char* lut = NULL;
    lut = (unsigned char*) malloc ( 16777216 * sizeof(unsigned char) );
    if ( !lut ) {
        fprintf(stderr, "Cannot allocate memory for LUT \n"); exit(-1);
        fflush(fp);
        fclose(fp);
    }

    unsigned long i = 0;
    int read = 0;
    while( !feof(fp) ) {
        unsigned char bits;
        read += fread( &bits, sizeof(unsigned char), 1, fp );
        for ( unsigned int j = 0, k=1; j < 8; j++, k*=2, i++ ) {
            if ( (bits & k) > 0 ) lut[i] = 1; else lut[i] = 0;
        }
    }

    if (read != 2097152) { fprintf(stderr, "Failed to read LUT \n"); exit(-1); }

    unsigned long nobject = 0;
    unsigned long index = 0;
    for ( int y = 0; y < img->height; y++ ) {
        for ( int x = 0; x < img->width; x++ ) {
            if ( img->data[ index ] != 0 ) {
                nobject++;
                img->data[index] = OBJECT;
            }
            index++;
        }
    }

    img->createBorder(3);

    fpta_thinning( img, lut, NULL );

    img->createBorder(-3);

    unsigned long nskel = 0;
    index = 0;
    for ( int y = 0; y < img->height; y++ ) {
        for ( int x = 0; x < img->width; x++ ) {
            if ( (img->data[index] & OBJECT) == OBJECT) {
                nskel++;
                iu_centers.push_back(index%img->width);
                iv_centers.push_back(index/img->width);
            }

            index++;
        }
    }

    delete img;

    free( lut );
    fflush(fp);
    fclose(fp);
}
