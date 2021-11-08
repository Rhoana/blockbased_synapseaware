import os 
import struct



from blockbased_synapseaware.utilities.constants import OR_X, OR_Y, OR_Z


class PointsFile:
	def __init__(self, volume_size, block_size, ):
		pass


block_size = [768, 768, 768]

old_block_size = [5, 5, 5]
new_block_size = [2, 2, 2]

point_types = ['surfaces', 'synapses']

for point_type in point_types:
	old_directory = '{}-old/JWR/{:04d}x{:04d}x{:04d}'.format(point_type, block_size[0], block_size[1], block_size[2])
	new_directory = '{}/JWR/{:04d}x{:04d}x{:04d}'.format(point_type, block_size[0], block_size[1], block_size[2])

	if not os.path.exists(new_directory):
		os.makedirs(new_directory, exist_ok = True)

	old_volume_size = [old_block_size[iv] * block_size[iv] for iv in range(3)]
	new_volume_size = [new_block_size[iv] * block_size[iv] for iv in range(3)]

	for filename in sorted(os.listdir(old_directory)):
		with open('{}/{}'.format(old_directory, filename), 'rb') as fd:
			volume_size = struct.unpack('qqq', fd.read(24))
			block_size = struct.unpack('qqq', fd.read(24))
			nneurons, = struct.unpack('q', fd.read(8))
			
			global_indices = {}
			local_indices = {}
			
			checksum = 0
			
			for ii in range(nneurons):
				label, = struct.unpack('q', fd.read(8))
				nvoxels, = struct.unpack('q', fd.read(8))
				
				global_indices[label] = list(struct.unpack('%sq' % nvoxels, fd.read(8 * nvoxels)))
				local_indices[label] = list(struct.unpack('%sq' % nvoxels, fd.read(8 * nvoxels)))
				
				checksum += (sum(global_indices[label] + local_indices[label]))
				
			input_checksum, = struct.unpack('q', fd.read(8))
			assert (input_checksum == checksum)

		updated_global_indices = {}
		updated_local_indices = {}
		
		# update the points
		for label in sorted(global_indices.keys()):
			updated_global_indices_array = []
			updated_local_indices_array = []

			# update the global and local indices 
			for (global_index, local_index) in zip(global_indices[label], local_indices[label]):
				global_iz = global_index // (old_volume_size[OR_Y] * old_volume_size[OR_X])
				global_iy = (global_index - global_iz * old_volume_size[OR_Y] * old_volume_size[OR_X]) // old_volume_size[OR_X]
				global_ix = global_index % old_volume_size[OR_X]
		
				if (global_iz >= new_volume_size[OR_Z]): continue 
				if (global_iy >= new_volume_size[OR_Y]): continue 
				if (global_ix >= new_volume_size[OR_X]): continue 
				
				global_index = global_iz * (new_volume_size[OR_Y] * new_volume_size[OR_X]) + global_iy * new_volume_size[OR_X] + global_ix 
				
				updated_global_indices_array.append(global_index)
				updated_local_indices_array.append(local_index)
				
			if not len(updated_global_indices_array): continue 
			
			updated_global_indices[label] = updated_global_indices_array
			updated_local_indices[label] = updated_local_indices_array
		
		if not len(updated_global_indices.keys()): continue
			
		with open('{}/{}'.format(new_directory, filename), 'wb') as fd:
			nlabels = len(updated_global_indices.keys())
			
			# write the header for the points file
			fd.write(struct.pack('qqq', *new_volume_size))
			fd.write(struct.pack('qqq', *block_size))
			fd.write(struct.pack('q', nlabels))

			# checksum for file verification
			checksum = 0

			for label in sorted(updated_global_indices.keys()):
				# write the header for this points chapter
				nvoxels = len(updated_global_indices[label])
				fd.write(struct.pack('qq', label, nvoxels))

				# write the global indices
				for global_index in updated_global_indices[label]:
					fd.write(struct.pack('q', global_index))
					checksum += global_index

				# write the local indices
				for local_index in updated_local_indices[label]:
					fd.write(struct.pack('q', local_index))
					checksum += local_index

			# write the checksum
			fd.write(struct.pack('q', checksum))
		
		print ('Wrote {}'.format(filename))
