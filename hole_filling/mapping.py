import time



from numba import jit, types
from numba.typed import Dict



from blockbased_synapseaware.utilities.dataIO import ReadH5File, ReadPickledData, WriteH5File



@jit(nopython=True)
def AssignBackgroundAssociatedLabels(components, associated_label_dict):
    zres, yres, xres = components.shape

    for iz in range(zres):
        for iy in range(yres):
            for ix in range(xres):
                if components[iz,iy,ix] < 0:
                    components[iz,iy,ix] = associated_label_dict[components[iz,iy,ix]]

    return components



def RemoveHoles(data, iz, iy, ix):
    # start timing statistics
    total_time = time.time()

    # read in the associated labels and the connected components
    read_time = time.time()
    components = ReadH5File('{}/components.h5'.format(data.TempComponentsDirectory(iz, iy, ix)))
    # need to first create separate empty numba Dict
    associated_label_dict = Dict.empty(key_type=types.int64, value_type=types.int64)
    associated_label_dict.update(ReadPickledData('{}/hole-filling-associated-labels.pickle'.format(data.TempDirectory())))
    read_time = time.time() - read_time

    # remove all the holes with the associated labels dictionary
    hole_fill_time = time.time()
    components = AssignBackgroundAssociatedLabels(components, associated_label_dict)
    hole_fill_time = time.time() - hole_fill_time

    # write the updated components to disk
    write_time = time.time()
    output_directory = data.HoleFillingOutputDirectory()
    output_filename = '{}/{:04d}z-{:04d}y-{:04d}x.h5'.format(output_directory, iz, iy, ix)
    WriteH5File(components, output_filename)
    write_time = time.time() - write_time

    total_time = time.time() - total_time

    print ('Read Time: {:0.2f} seconds.'.format(read_time))
    print ('Hole Fill Time: {:0.2f} seconds.'.format(hole_fill_time))
    print ('Write Time: {:0.2f} seconds.'.format(write_time))
    print ('Total Time: {:0.2f} seconds.'.format(total_time))
