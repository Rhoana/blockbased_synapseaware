import h5py
import pickle



from blockbased_synapseaware.data_structures.meta_data import MetaData



def ReadMetaData(prefix):
    return MetaData(prefix)



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
