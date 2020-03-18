import time



from blockbased_synapseaware.utilities.dataIO import WriteH5File



def SaveAnchorWalls(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # read in the original segmentation
    read_time = time.time()
    segmentation = data.ReadSegmentationBlock(iz, iy, ix)
    read_time = time.time() - read_time
    
    # write the walls for the segmentation to file
    write_time = time.time()

    # get the temp directory for this block
    tmp_directory = data.TempComponentsDirectory(iz, iy, ix)
    
    WriteH5File(segmentation[0,:,:], '{}/z-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[-1,:,:], '{}/z-max-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,0,:], '{}/y-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,-1,:], '{}/y-max-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,:,0], '{}/x-min-anchor-points.h5'.format(tmp_directory))
    WriteH5File(segmentation[:,:,-1], '{}/x-max-anchor-points.h5'.format(tmp_directory))
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
