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

namespace cc3d {

template <typename T>
class DisjointSet {

private:
  std::unordered_map<T,T> ids;

public:

  DisjointSet () {
    ids = std::unordered_map<T,T>();
  }

  ~DisjointSet () {
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

// This is the original Wu et al decision tree but without
// any copy operations, only union find. We can decompose the problem
// into the z - 1 problem unified with the original 2D algorithm.
// If literally none of the Z - 1 are filled, we can use a faster version
// of this that uses copies.
template <typename T>
inline void unify2d(
    const int64_t loc, const T cur,
    const int64_t x, const int64_t y,
    const int64_t sx, const int64_t sy,
    const T* in_labels, const int64_t *out_labels,
    DisjointSet<int64_t> &equivalences
  ) {

  if (y > 0 && cur == in_labels[loc - sx]) {
    equivalences.unify(out_labels[loc], out_labels[loc - sx]);
  }
  else if (x > 0 && cur == in_labels[loc - 1]) {
    equivalences.unify(out_labels[loc], out_labels[loc - 1]);

    if (x < sx - 1 && y > 0 && cur == in_labels[loc + 1 - sx]) {
      equivalences.unify(out_labels[loc], out_labels[loc + 1 - sx]);
    }
  }
  else if (x > 0 && y > 0 && cur == in_labels[loc - 1 - sx]) {
    equivalences.unify(out_labels[loc], out_labels[loc - 1 - sx]);

    if (x < sx - 1 && y > 0 && cur == in_labels[loc + 1 - sx]) {
      equivalences.unify(out_labels[loc], out_labels[loc + 1 - sx]);
    }
  }
  else if (x < sx - 1 && y > 0 && cur == in_labels[loc + 1 - sx]) {
    equivalences.unify(out_labels[loc], out_labels[loc + 1 - sx]);
  }
}

template <typename T>
inline void unify2d_rt(
    const int64_t loc, const T cur,
    const int64_t x, const int64_t y,
    const int64_t sx, const int64_t sy,
    const T* in_labels, const int64_t *out_labels,
    DisjointSet<int64_t> &equivalences
  ) {

  if (x < sx - 1 && y > 0 && cur == in_labels[loc + 1 - sx]) {
    equivalences.unify(out_labels[loc], out_labels[loc + 1 - sx]);
  }
}

template <typename T>
inline void unify2d_lt(
    const int64_t loc, const T cur,
    const int64_t x, const int64_t y,
    const int64_t sx, const int64_t sy,
    const T* in_labels, const int64_t *out_labels,
    DisjointSet<int64_t> &equivalences
  ) {

  if (x > 0 && cur == in_labels[loc - 1]) {
    equivalences.unify(out_labels[loc], out_labels[loc - 1]);
  }
  else if (x > 0 && y > 0 && cur == in_labels[loc - 1 - sx]) {
    equivalences.unify(out_labels[loc], out_labels[loc - 1 - sx]);
  }
}

// This is the second raster pass of the two pass algorithm family.
// The input array (output_labels) has been assigned provisional
// labels and this resolves them into their final labels. We
// modify this pass to also ensure that the output labels are
// numbered from 1 sequentially.
int64_t* relabel(
    int64_t* out_labels, const int64_t voxels,
    const int64_t num_labels, DisjointSet<int64_t> &equivalences
  ) {

  int64_t label;
  int64_t* renumber = new int64_t[(num_labels*-1)+1]();
  int64_t next_label = -1;

  // Raster Scan 2: Write final labels based on equivalences
  for (int64_t loc = 0; loc < voxels; loc++) {
    if (out_labels[loc]>0) {
      continue;
    }

    label = equivalences.root(out_labels[loc]*-1)*-1;

    if (renumber[label*-1]) {
      out_labels[loc] = renumber[label*-1]*-1;
    }
    else {
      renumber[label*-1] = next_label*-1;
      out_labels[loc] = next_label;
      next_label--;
    }
  }

  delete[] renumber;

  // double max_label = *std::max_element(out_labels, out_labels+voxels);
  // printf("Max label labels_out is: %ld\n", (long)(*std::max_element(out_labels, out_labels+voxels)));

  return out_labels;
}

template <typename T>
int64_t* connected_components3d_6(
    T* in_labels,
    const int64_t sx, const int64_t sy, const int64_t sz,
    int64_t start_label, int64_t *out_labels = NULL
  ) {

  const int64_t sxy = sx * sy;
  const int64_t voxels = sxy * sz;

  DisjointSet<int64_t> equivalences();

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
          next_label--;
          out_labels[loc] = next_label;
          equivalences.add(out_labels[loc]*-1);
        }
      }
    }
  }

  return relabel(out_labels, voxels, next_label, equivalences);
}

template <typename T>
int64_t* connected_components3d(
    T* in_labels,
    const int64_t sx, const int64_t sy, const int64_t sz,
    int64_t start_label, const int64_t connectivity,
    int64_t *out_labels = NULL
  ) {

  if (connectivity == 6) {
    return connected_components3d_6<T>(
      in_labels, sx, sy, sz,
      start_label, out_labels
    );
  }
  else {
    throw "Only 6 connectivity is supported!";
  }
}

};

#endif
