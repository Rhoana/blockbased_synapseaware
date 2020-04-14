import h5py
import struct
import pickle



import numpy as np



from blockbased_synapseaware.data_structures.meta_data import MetaData



def ReadMetaData(meta_filename):
    return MetaData(meta_filename)



def ReadH5File(filename):
    with h5py.File(filename, 'r') as hf:
        data = np.array(hf[list(hf.keys())[0]])

    return data



def WriteH5File(data, filename):
    with h5py.File(filename, 'w') as hf:
        hf.create_dataset('main', data=data, compression='gzip')



def PickleData(data, filename):
    with open(filename, 'wb') as fd:
        pickle.dump(data, fd)



def PickleNumbaData(data, filename):
    # convert the numba data into a normal dict
    temp = dict()
    temp.update(data)

    PickleData(temp, filename)



def ReadPickledData(filename):
    with open(filename, 'rb') as fd:
        return pickle.load(fd)



def ReadPtsFile(data, filename):
    # open the file
    with open(filename, 'rb') as fd:
        # read the header
        volume_size = struct.unpack('qqq', fd.read(24))
        block_size = struct.unpack('qqq', fd.read(24))
        nlabels, = struct.unpack('q', fd.read(8))

        # assert the header matches the current data info
        assert (volume_size == data.VolumeSize())
        assert (block_size == data.BlockSize())

        # create dictionaries for the global and local indices
        global_indices = {}
        local_indices = {}

        # check sum confirms proper I/O
        checksum = 0

        # iterate through all labels in this volume
        for _ in range(nlabels):
            label, nvoxels, = struct.unpack('qq', fd.read(16))

            # read in the global and local indices
            global_indices[label] = list(struct.unpack('%sq' % nvoxels, fd.read(8 * nvoxels)))
            local_indices[label] = list(struct.unpack('%sq' % nvoxels, fd.read(8 * nvoxels)))

            checksum += sum(global_indices[label] + local_indices[label])

        # verify the check sum
        input_checksum, = struct.unpack('q', fd.read(8))
        assert (input_checksum == checksum)

    return global_indices, local_indices



def ReadAttributePtsFile(data, filename):
    # open the file
    with open(filename, 'rb') as fd:
        # read the header
        volume_size = struct.unpack('qqq', fd.read(24))
        block_size = struct.unpack('qqq', fd.read(24))
        nlabels, = struct.unpack('q', fd.read(8))

        # assert the header matches the current data info
        assert (volume_size == data.VolumeSize())
        assert (block_size == data.BlockSize())
        assert (nlabels == 1)

        # create dictionaries for the global indicies
        global_indices = {}

        for _ in range(nlabels):
            label, nvoxels, = struct.unpack('qq', fd.read(16))

            # get the global index and corresponding attribute for each voxel
            for _ in range(nvoxels):
                global_index, attribute_value, = struct.unpack('qf', fd.read(12))

                global_indices[global_index] = attribute_value

    return global_indices, label



def WritePtsFile(data, filename, points, block_index = None, input_local_indices = True):
    # if local indices are given, need to know block index
    if (input_local_indices == True): assert (not block_index == None)

    # get the number of labels
    labels = sorted(points.keys())

    # write the header
    volume_size = data.VolumeSize()
    block_size = data.BlockSize()
    nlabels = len(labels)

    with open(filename, 'wb') as fd:
        # write the header for the points file
        fd.write(struct.pack('qqq', *volume_size))
        fd.write(struct.pack('qqq', *block_size))
        fd.write(struct.pack('q', nlabels))

        # checksum for file verification
        checksum = 0

        for label in labels:
            # write the header for this points chapter
            nvoxels = len(points[label])
            fd.write(struct.pack('qq', label, nvoxels))

            global_indices = []
            local_indices = []

            # get the local and global index
            for voxel_index in points[label]:
                if input_local_indices:
                    global_indices.append(data.LocalIndexToGlobalIndex(voxel_index, block_index))
                    local_indices.append(voxel_index)
                else:
                    global_indices.append(voxel_index)
                    local_indices.append(data.GlobalIndexToLocalIndex(voxel_index))

            # write the global indices
            for global_index in global_indices:
                fd.write(struct.pack('q', global_index))
                checksum += global_index

            # write the local indices
            for local_index in local_indices:
                fd.write(struct.pack('q', local_index))
                checksum += local_index

        # write the checksum
        fd.write(struct.pack('q', checksum))



def WriteAttributePtsFile(data, filename, label, attributes):
    # retrieve header information
    volume_size = data.VolumeSize()
    block_size = data.BlockSize()
    # there is only one label in attributes files
    nlabels = 1

    # open the file
    with open(filename, 'wb') as fd:
        # write the header
        fd.write(struct.pack('qqq', *volume_size))
        fd.write(struct.pack('qqq', *block_size))
        fd.write(struct.pack('q', nlabels))

        # number of voxels with corresponding attributes
        nvoxels = len(attributes.keys())

        # write the label and number of voxels
        fd.write(struct.pack('q', label))
        fd.write(struct.pack('q', nvoxels))

        # write each global index with its corresponding attribute
        for (voxel_index, attribute) in attributes.items():
            fd.write(struct.pack('q', voxel_index))
            fd.write(struct.pack('f', attribute))
