"""
Cython binding for connected components applied to 3D images
with 26-connectivity and handling for multiple labels.

Author: William Silversmith
Affiliation: Seung Lab, Princeton Neuroscience Institute
Date: August 2018 - June 2019

---
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
---

If you received a copy of this program in binary form, you can get
the source code for free here:

https://github.com/seung-lab/connected-components-3d
"""

from libc.stdlib cimport calloc, free
from libc.stdint cimport (
  int8_t, int16_t, int32_t, int64_t,
  uint8_t, uint16_t, uint32_t, uint64_t,
)
from cpython cimport array
import array
import sys

from libcpp.vector cimport vector
cimport numpy as cnp
import numpy as np

__VERSION__ = '1.4.1'

cdef extern from "cc3d.hpp" namespace "cc3d":
  cdef int64_t* connected_components3d[T](
    T* in_labels,
    int64_t sx, int64_t sy, int64_t sz,
    int64_t start_label, int64_t connectivity,
    int64_t* out_labels
  )

ctypedef fused INTEGER:
  uint8_t
  uint16_t
  uint32_t
  uint64_t
  int8_t
  int16_t
  int32_t
  int64_t

class DimensionError(Exception):
  """The array has the wrong number of dimensions."""
  pass

def connected_components(data, int64_t start_label=-1, int64_t connectivity=6):
  """
  ndarray connected_components(data, int64_t start_label=-1, int64_t connectivity=6)

  Connected components applied to 3D images with
  handling for multiple labels.

  Required:
    data: Input weights in a 2D or 3D numpy array.
  Optional:
    start_label (int): start label for the background components, which will be labeled in decreasing order
    connectivity (int): 6 (voxel faces)

  Returns: 2D or 3D numpy array remapped to reflect
    the connected components.
  """
  dims = len(data.shape)
  if dims not in (1,2,3):
    raise DimensionError("Only 1D, 2D, and 3D arrays supported. Got: " + str(dims))

  if connectivity != 6:
    raise ValueError("Only 6 connectivitiy is supported! Got: " + str(connectivity))

  if data.size == 0:
    return np.zeros(shape=(0,), dtype=np.int64)

  order = 'F' if data.flags['F_CONTIGUOUS'] else 'C'

  while len(data.shape) < 3:
    if order == 'C':
      data = data[np.newaxis, ...]
    else: # F
      data = data[..., np.newaxis ]

  if not data.flags['C_CONTIGUOUS'] and not data.flags['F_CONTIGUOUS']:
    data = np.copy(data, order=order)

  shape = list(data.shape)

  # The default C order of 4D numpy arrays is (channel, depth, row, col)
  # col is the fastest changing index in the underlying buffer.
  # fpzip expects an XYZC orientation in the array, namely nx changes most rapidly.
  # Since in this case, col is the most rapidly changing index,
  # the inputs to fpzip should be X=col, Y=row, Z=depth, F=channel
  # If the order is F, the default array shape is fine.
  if order == 'C':
    shape.reverse()

  cdef int sx = shape[0]
  cdef int sy = shape[1]
  cdef int sz = shape[2]

  cdef uint8_t[:,:,:] arr_memview8u
  cdef uint16_t[:,:,:] arr_memview16u
  cdef uint32_t[:,:,:] arr_memview32u
  cdef uint64_t[:,:,:] arr_memview64u
  cdef int8_t[:,:,:] arr_memview8
  cdef int16_t[:,:,:] arr_memview16
  cdef int32_t[:,:,:] arr_memview32
  cdef int64_t[:,:,:] arr_memview64

  cdef uint64_t voxels = <uint64_t>sx * <uint64_t>sy * <uint64_t>sz
  cdef cnp.ndarray[int64_t, ndim=1] out_labels = np.zeros( (voxels,), dtype=np.int64, order='C' )

  if start_label >= 0:
    raise ValueError("Start label has to be smaller than 0")

  dtype = data.dtype

  if dtype == np.uint64:
    arr_memview64u = data
    labels = connected_components3d[uint64_t](
      &arr_memview64u[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.uint32:
    arr_memview32u = data
    labels = connected_components3d[uint32_t](
      &arr_memview32u[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.uint16:
    arr_memview16u = data
    labels = connected_components3d[uint16_t](
      &arr_memview16u[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype in (np.uint8, np.bool):
    arr_memview8u = data.astype(np.uint8)
    labels = connected_components3d[uint8_t](
      &arr_memview8u[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.int64:
    arr_memview64 = data
    labels = connected_components3d[int64_t](
      &arr_memview64[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.int32:
    arr_memview32 = data
    labels = connected_components3d[int32_t](
      &arr_memview32[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.int16:
    arr_memview16 = data
    labels = connected_components3d[int16_t](
      &arr_memview16[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  elif dtype == np.int8:
    arr_memview8 = data
    labels = connected_components3d[int8_t](
      &arr_memview8[0,0,0],
      sx, sy, sz, start_label, connectivity,
      <int64_t*>&out_labels[0]
    )
  else:
    raise TypeError("Type {} not currently supported.".format(dtype))

  if dims == 3:
    if order == 'C':
      return out_labels.reshape( (sz, sy, sx), order=order)
    else:
      return out_labels.reshape( (sx, sy, sz), order=order)
  elif dims == 2:
    if order == 'C':
      return out_labels.reshape( (sy, sx), order=order)
    else:
      return out_labels.reshape( (sx, sy), order=order)
  else:
    return out_labels.reshape( (sx), order=order)
