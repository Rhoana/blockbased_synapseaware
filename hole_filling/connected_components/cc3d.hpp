/*
 * Connected Components for 3D images.
 * Implments a 3D variant of the two pass algorithim by
 * Rosenfeld and Pflatz augmented with Union-Find and a decision
 * tree influenced by the work of Wu et al.
 *
 * Essentially, you raster scan, and every time you first encounter
 * a foreground pixel, mark it with a new label if the pixels to its
 * top and left are background. If there is a preexisting label in its
 * neighborhood, use that label instead. Whenever you see that two labels
 * are adjacent, record that we should unify them in the next pass. This
 * equivalency table can be constructed in several ways, but we've choseen
 * to use Union-Find with full path compression.
 *
 * We also use a decision tree that aims to minimize the number of expensive
 * unify operations and replaces them with simple label copies when valid.
 *
 * In the next pass, the pixels are relabeled using the equivalency table.
 * Union-Find (disjoint sets) establishes one label as the root label of a
 * tree, and so the root is considered the representative label. Each pixel
 * is labeled with the representative label. The representative labels
 * are themselves remapped into an increasing consecutive sequence
 * starting from one.
 *
 * Author: William Silversmith
 * Affiliation: Seung Lab, Princeton University
 * Date: August 2018 - June 2019
 *
 * ----
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * ----
 */

#ifndef CC3D_HPP
#define CC3D_HPP

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <unordered_map>
#include <iostream>

namespace cc3d {

// DisjointSet and renumber structure can either be implemented as an unordered_map or a simple array.
// Arrays are higher in memory consumption but faster, whereas unordered_maps are lower in memory (as entries are sparse) but have a longer runtime.
// set this bool true to use the unordered_map implementation and false to use the (original) array implementation
bool UseUOMap = 0;

template <typename T>
class DisjointSet_Map {

private:
  std::unordered_map<T,T> ids;

public:

  DisjointSet_Map () {
    ids = std::unordered_map<T,T>();
  }

  ~DisjointSet_Map () {
    ids.clear();
  }

  T root (T n) {
    T parent = ids[n];
    while (parent != ids[parent]) {
      ids[parent] = ids[ids[parent]]; // path compression
      parent = ids[parent];
    }

    return parent;
  }

  bool find (T p, T q) {
    return root(p) == root(q);
  }

  void add(T p) {

    if (ids.find(p)==ids.end())
      ids[p]=p;

  }

  void unify (T p, T q) {
    if (p == q) {
      return;
    }

    T i = root(p);
    T j = root(q);

    if (i == 0) {
      add(p);
      i = p;
    }

    if (j == 0) {
      add(q);
      j = q;
    }

    ids[i] = j;
  }

  void print() {
    for (int i = 0; i < 15; i++) {
      printf("%d, ", ids[i]);
    }
    printf("\n");
  }

  // would be easy to write remove.
  // Will be O(n).
};

template <typename T>
class DisjointSet_Arr {
public:
  T *ids;
  size_t length;

  DisjointSet_Arr () {
    length = 65536;
    ids = new T[length]();
  }

  DisjointSet_Arr (size_t len) {
    length = len;
    ids = new T[length]();
  }

  ~DisjointSet_Arr () {
    delete []ids;
  }

  T root (T n) {
    T parent = ids[n];
    while (parent != ids[parent]) {
      ids[parent] = ids[ids[parent]]; // path compression
      parent = ids[parent];
    }

    return parent;
  }

  bool find (T p, T q) {
    return root(p) == root(q);
  }

  void add(T p) {
    if (p >= length) {
      //printf("Connected Components Error: Label %d cannot be mapped to union-find array of length %d.\n", p, length);
      throw "maximum length exception";
    }

    if (ids[p] == 0) {
      ids[p] = p;
    }
  }

  void unify (T p, T q) {
    if (p == q) {
      return;
    }

    T i = root(p);
    T j = root(q);

    if (i == 0) {
      add(p);
      i = p;
    }

    if (j == 0) {
      add(q);
      j = q;
    }

    ids[i] = j;
  }

  void print() {
    for (int i = 0; i < 15; i++) {
      printf("%d, ", ids[i]);
    }
    printf("\n");
  }

  // would be easy to write remove.
  // Will be O(n).
};


// This is the second raster pass of the two pass algorithm family.
// The input array (output_labels) has been assigned provisional
// labels and this resolves them into their final labels. We
// modify this pass to also ensure that the output labels are
// numbered from 1 sequentially.

int64_t* relabel_Map(
    int64_t* out_labels, const int64_t voxels, int64_t start_label,
    DisjointSet_Map<int64_t> &equivalences
  ) {

  int64_t label;

  std::unordered_map<int64_t,int64_t> renumber = std::unordered_map<int64_t,int64_t>();

  int64_t next_label = start_label;

  // Raster Scan 2: Write final labels based on equivalences
  for (int64_t loc = 0; loc < voxels; loc++) {
    if (out_labels[loc]>0) {
      continue;
    }

    label = equivalences.root(out_labels[loc]*-1)*-1;

    if (renumber.find(label*-1)!=renumber.end()) {
      out_labels[loc] = renumber[label*-1]*-1;
    }

    else {
      renumber[label*-1] = next_label*-1;
      out_labels[loc] = next_label;
      next_label--;
    }
  }

  renumber.clear();

  return out_labels;
}

int64_t* relabel_Arr(
    int64_t* out_labels, const int64_t voxels, int64_t start_label,
    int64_t max_label, DisjointSet_Arr<int64_t> &equivalences
  ) {

  int64_t label;
  int64_t num_labels = -1*max_label - 1;
  int64_t* renumber = new int64_t[num_labels+1]();
  int64_t next_label = -1;

  // Raster Scan 2: Write final labels based on equivalences
  for (int64_t loc = 0; loc < voxels; loc++) {
    if (out_labels[loc]>0) {
      continue;
    }

    label = equivalences.root(out_labels[loc]*-1)*-1;

    if (renumber[label*-1]) {
      out_labels[loc] = renumber[label*-1]*-1+start_label+1;
    }
    else {
      renumber[label*-1] = next_label*-1;
      out_labels[loc] = next_label+start_label+1;
      next_label--;
    }
  }

  delete[] renumber;

  return out_labels;
}

template <typename T>
int64_t* connected_components3d_6_Map(
    T* in_labels,
    const int64_t sx, const int64_t sy, const int64_t sz,
    int64_t start_label, int64_t *out_labels = NULL
  ) {

  const int64_t sxy = sx * sy;
  const int64_t voxels = sxy * sz;

  DisjointSet_Map<int64_t> equivalences;

  if (out_labels == NULL) {
    out_labels = new int64_t[voxels]();
  }

  /*
    Layout of forward pass mask (which faces backwards).
    N is the current location.

    z = -1     z = 0
    A B C      J K L   y = -1
    D E F      M N     y =  0
    G H I              y = +1
   -1 0 +1    -1 0   <-- x axis
  */

  // Z - 1
  const int64_t E = -sxy;

  // Current Z
  const int64_t K = -sx;
  const int64_t M = -1;
  // N = 0;

  int64_t loc = 0;
  int64_t next_label = start_label;

  // Raster Scan 1: Set temporary labels and
  // record equivalences in a disjoint set.

  for (int64_t z = 0; z < sz; z++) {
    for (int64_t y = 0; y < sy; y++) {
      for (int64_t x = 0; x < sx; x++) {
        loc = x + sx * (y + sy * z);

        const T cur = in_labels[loc];

        if (cur > 0) {
          out_labels[loc]=cur;
          continue;
        }

        if (x > 0 && cur == in_labels[loc + M]) {
          out_labels[loc] = out_labels[loc + M];

          if (y > 0 && cur == in_labels[loc + K]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + K]*-1);
          }
          if (z > 0 && cur == in_labels[loc + E]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + E]*-1);
          }
        }
        else if (y > 0 && cur == in_labels[loc + K]) {
          out_labels[loc] = out_labels[loc + K];

          if (z > 0 && cur == in_labels[loc + E]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + E]*-1);
          }
        }
        else if (z > 0 && cur == in_labels[loc + E]) {
          out_labels[loc] = out_labels[loc + E];
        }
        else {
          out_labels[loc] = next_label;
          equivalences.add(out_labels[loc]*-1);
          next_label--;
        }
      }
    }
  }

  return relabel_Map(out_labels, voxels, start_label, equivalences);
}

template <typename T>
int64_t* connected_components3d_6_Arr(
    T* in_labels,
    const int64_t sx, const int64_t sy, const int64_t sz,
    int64_t start_label, int64_t *out_labels = NULL
  ) {

  const int64_t sxy = sx * sy;
  const int64_t voxels = sxy * sz;

  DisjointSet_Arr<int64_t> equivalences(voxels);

  if (out_labels == NULL) {
    out_labels = new int64_t[voxels]();
  }

  /*
    Layout of forward pass mask (which faces backwards).
    N is the current location.

    z = -1     z = 0
    A B C      J K L   y = -1
    D E F      M N     y =  0
    G H I              y = +1
   -1 0 +1    -1 0   <-- x axis
  */

  // Z - 1
  const int64_t E = -sxy;

  // Current Z
  const int64_t K = -sx;
  const int64_t M = -1;
  // N = 0;

  int64_t loc = 0;
  int64_t next_label = -1;

  // Raster Scan 1: Set temporary labels and
  // record equivalences in a disjoint set.

  for (int64_t z = 0; z < sz; z++) {
    for (int64_t y = 0; y < sy; y++) {
      for (int64_t x = 0; x < sx; x++) {
        loc = x + sx * (y + sy * z);

        const T cur = in_labels[loc];

        if (cur > 0) {
          out_labels[loc]=cur;
          continue;
        }

        if (x > 0 && cur == in_labels[loc + M]) {
          out_labels[loc] = out_labels[loc + M];

          if (y > 0 && cur == in_labels[loc + K]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + K]*-1);
          }
          if (z > 0 && cur == in_labels[loc + E]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + E]*-1);
          }
        }
        else if (y > 0 && cur == in_labels[loc + K]) {
          out_labels[loc] = out_labels[loc + K];

          if (z > 0 && cur == in_labels[loc + E]) {
            equivalences.unify(out_labels[loc]*-1, out_labels[loc + E]*-1);
          }
        }
        else if (z > 0 && cur == in_labels[loc + E]) {
          out_labels[loc] = out_labels[loc + E];
        }
        else {
          out_labels[loc] = next_label;
          equivalences.add(out_labels[loc]*-1);
          next_label--;
        }
      }
    }
  }

  return relabel_Arr(out_labels, voxels, start_label, next_label, equivalences);
}

template <typename T>
int64_t* connected_components3d(
    T* in_labels,
    const int64_t sx, const int64_t sy, const int64_t sz,
    int64_t start_label, const int64_t connectivity,
    int64_t *out_labels = NULL
  ) {

  if (connectivity == 6) {

    if (UseUOMap){
      return connected_components3d_6_Map<T>(
        in_labels, sx, sy, sz,
        start_label, out_labels
      );
    }
    else {
      return connected_components3d_6_Arr<T>(
        in_labels, sx, sy, sz,
        start_label, out_labels
      );
    }
  }
  else {
    throw "Only 6 connectivity is supported!";
  }
}

};

#endif
