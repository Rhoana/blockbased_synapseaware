import os
import statistics



import numpy as np



import scipy.stats



import matplotlib
from matplotlib import pyplot as plt

# set matplotlib styles
plt.style.use('seaborn-white')



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPickledData, PickleData



million = 10 ** 6



def ParseLine(line):
    # return the time in seconds for this line
    return float(line.split(':')[1].strip().split()[0])



def PrintStatistics(title, times, wfd):
    avg = statistics.mean(times)
    stddev = statistics.stdev(times)

    print ('  {:45s} {:10.2f} seconds (\u00B1{:0.2f})'.format(title, avg, stddev))
    wfd.write('  {:45s} {:10.2f} seconds (\u00B1{:0.2f})\n'.format(title, avg, stddev))


def ConnectedComponents(data, wfd):
    timing_directory = '{}/connected-components'.format(data.TimingDirectory())

    read_times = []
    components_times = []
    adjacency_set_times = []
    background_components_associated_labels_times = []
    write_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    components_times.append(ParseLine(rfd.readline()))
                    adjacency_set_times.append(ParseLine(rfd.readline()))
                    background_components_associated_labels_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Connected Components')
    wfd.write('Connected Components\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Components Time', components_times, wfd)
    PrintStatistics('Adjacency Set Time', adjacency_set_times, wfd)
    PrintStatistics('Background Components Associated Labels Time', background_components_associated_labels_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def ConnectLabelsAcrossBlocks(data, wfd):
    timing_directory = '{}/connect-labels-across-blocks'.format(data.TimingDirectory())

    adjacency_set_times = []
    write_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    adjacency_set_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Connect Labels Across Blocks')
    wfd.write('Connect Labels Across Blocks\n')

    PrintStatistics('Adjacency Set Time', adjacency_set_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def CombineAssociatedLabels(data, wfd):
    timing_directory = data.TimingDirectory()

    timing_filename = '{}/combine-associated-labels.txt'.format(timing_directory)

    with open(timing_filename, 'r') as rfd:
        read_time = ParseLine(rfd.readline())
        adjacency_set_time = ParseLine(rfd.readline())
        write_time = ParseLine(rfd.readline())
        total_time = ParseLine(rfd.readline())

    print ('Combine Associated Labels')
    print ('  {:45s} {:10.2f} seconds'.format('Read Time', read_time))
    print ('  {:45s} {:10.2f} seconds'.format('Adjacency Set Time', adjacency_set_time))
    print ('  {:45s} {:10.2f} seconds'.format('Write Time', write_time))
    print ('  {:45s} {:10.2f} seconds'.format('Total Time', total_time))

    wfd.write('Combine Associated Labels\n')
    wfd.write('  {:45s} {:10.2f} seconds\n'.format('Read Time', read_time))
    wfd.write('  {:45s} {:10.2f} seconds\n'.format('Adjacency Set Time', adjacency_set_time))
    wfd.write('  {:45s} {:10.2f} seconds\n'.format('Write Time', write_time))
    wfd.write('  {:45s} {:10.2f} seconds\n'.format('Total Time', total_time))

    return {'Total': total_time}



def FillHoles(data, wfd):
    timing_directory = '{}/fill-holes'.format(data.TimingDirectory())

    read_times = []
    hole_fill_times = []
    write_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    hole_fill_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Fill Holes')
    wfd.write('Fill Holes\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Hole Fill Time', hole_fill_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def SaveAnchorWalls(data, wfd):
    timing_directory = '{}/save-anchor-walls'.format(data.TimingDirectory())

    read_times = []
    write_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Save Anchor Walls')
    wfd.write('Save Anchor Walls\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def ComputeAnchorPoints(data, wfd):
    timing_directory = '{}/compute-anchor-points'.format(data.TimingDirectory())

    z_anchor_computation_times = []
    y_anchor_computation_times = []
    x_anchor_computation_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    z_anchor_computation_times.append(ParseLine(rfd.readline()))
                    y_anchor_computation_times.append(ParseLine(rfd.readline()))
                    x_anchor_computation_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Compute Anchor Points')
    wfd.write('Compute Anchor Points\n')

    PrintStatistics('Z Anchor Computation Time', z_anchor_computation_times, wfd)
    PrintStatistics('Y Anchor Computation Time', y_anchor_computation_times, wfd)
    PrintStatistics('X Anchor Computation Time', x_anchor_computation_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def TopologicalThinning(data, wfd):
    timing_directory = '{}/topological-thinning'.format(data.TimingDirectory())

    read_times = []
    thinning_times = []
    total_times = {}

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    thinning_times.append(ParseLine(rfd.readline()))
                    total_times[(iz, iy, ix)] = ParseLine(rfd.readline())

    print ('Topological Thinning')
    wfd.write('Topological Thinning\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Thinning Time', thinning_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def SkeletonRefinement(data, wfd):
    timing_directory = '{}/skeleton-refinement'.format(data.TimingDirectory())

    refinement_times = []
    updated_widths_times = []
    total_times = {}

    for label in range(1, data.NLabels()):
        timing_filename = '{}/{:016d}.txt'.format(timing_directory, label)
        if not os.path.exists(timing_filename): continue

        with open(timing_filename, 'r') as rfd:
            refinement_times.append(ParseLine(rfd.readline()))
            updated_widths_times.append(ParseLine(rfd.readline()))
            total_times[label] = ParseLine(rfd.readline())

    print ('Skeleton Refinement')
    wfd.write('Skeleton Refinement\n')

    PrintStatistics('Refinement Time', refinement_times, wfd)
    PrintStatistics('Update Widths Time', updated_widths_times, wfd)
    PrintStatistics('Total Time', total_times.values(), wfd)

    return total_times



def WallTime(data, times, m_cpus, strategy = 'FIFO'):
    # create an array of empty cpus
    cpu_times = np.zeros(m_cpus, dtype=np.float32)

    # these tasks must be completed (no variation of input in naive order)
    if not data.HoleFillingOutputDirectory() == None:
        tasks = ['components', 'connect-labels', 'combine-labels', 'fill-holes']
    else:
        tasks = []
    tasks += ['save-anchor-walls', 'compute-anchor-points', 'topological-thinning', 'skeleton-refinement']

    # create the order of jobs in a naive FIFO fashion where the times are determined by block index
    jobs = []

    # iterate over all tasks
    for task in tasks:
        # iterate over every time for this task (already in block index order)
        if strategy == 'FIFO':
            for time in times[task].values():
                jobs.append(time)
        elif strategy == 'LPT':
            for time in sorted(times[task].values(), reverse=True):
                jobs.append(time)

    # each job is placed on the cpu with the lowest time
    for job in jobs:
        idle_cpu = np.argmin(cpu_times)

        # this job is now allocated to the first idle cpu
        cpu_times[idle_cpu] += job

    return np.max(cpu_times)



def ComputeParallelStatistics(data, times):
    nzblocks, nyblocks, nxblocks = data.NBlocks()
    nblocks = nzblocks * nyblocks * nxblocks

    # get the frequency of cpus
    freq = nblocks // 10
    if not freq: freq = 1

    cpus = [cpu for cpu in range(1, nblocks, freq)]
    if not nblocks in cpus:
        cpus.append(nblocks)

    figures_directory = data.FiguresDirectory()
    if not os.path.exists(figures_directory):
        os.makedirs(figures_directory, exist_ok=True)
    timing_filename = '{}/cpu-statistics.txt'.format(figures_directory)
    fd = open(timing_filename, 'w')

    # calculate the amount of time needed with a naive heuristic (FIFO)
    for m_cpus in cpus:
        print ('No. CPUs: {}'.format(m_cpus))
        fd.write('No. CPUs: {}\n'.format(m_cpus))

        wall_time = WallTime(data, times, m_cpus, strategy = 'FIFO')
        print ('  FIFO Strategy: {:0.2f} seconds'.format(wall_time))
        fd.write('  FIFO Strategy: {:0.2f} seconds\n'.format(wall_time))

        wall_time = WallTime(data, times, m_cpus, strategy = 'LPT')
        print ('  LPT Strategy: {:0.2f} seconds'.format(wall_time))
        fd.write('  LPT Strategy: {:0.2f} seconds\n'.format(wall_time))



def ConductEndToEndTimingAnalysis(meta_filename):
    # run analysis for this dataset
    data = ReadMetaData(meta_filename)

    assert (not data.FiguresDirectory() == None)

    figures_directory = data.FiguresDirectory()
    if not os.path.exists(figures_directory):
        os.makedirs(figures_directory, exist_ok=True)
    timing_filename = '{}/timing-statistics.txt'.format(figures_directory)
    fd = open(timing_filename, 'w')

    # collect the timing statistics for all blocks
    times = {}

    # hole filling
    if not data.HoleFillingOutputDirectory() == None:
        times['components'] = ConnectedComponents(data, fd)
        times['connect-labels'] = ConnectLabelsAcrossBlocks(data, fd)
        times['combine-labels'] = CombineAssociatedLabels(data, fd)
        times['fill-holes'] = FillHoles(data, fd)

        # create aggregate stats
        times['hole-filling'] = {}
        for key in times['components']:
            # ignore the combine-labels time since it is a global operation
            times['hole-filling'][key] = times['components'][key] + times['connect-labels'][key] + times['fill-holes'][key]

    # skeleton generation
    times['save-anchor-walls'] = SaveAnchorWalls(data, fd)
    times['compute-anchor-points'] = ComputeAnchorPoints(data, fd)
    times['topological-thinning'] = TopologicalThinning(data, fd)
    times['skeleton-refinement'] = SkeletonRefinement(data, fd)

    # create aggregate stats
    times['skeletonization'] = {}
    for key in times['save-anchor-walls']:
        # ignore the skeleton refinement time since it is a global operation
        times['skeletonization'][key] = times['save-anchor-walls'][key] + times['compute-anchor-points'][key] + times['topological-thinning'][key]

    # close the timing file
    fd.close()

    timing_filename = '{}/timing-statistics-aggregates.txt'.format(figures_directory)
    with open(timing_filename, 'w') as fd:

        print ()

        if not data.HoleFillingOutputDirectory() == None:
            components_time = sum(times['components'].values())
            connect_labels_time = sum(times['connect-labels'].values())
            combine_labels_time = sum(times['combine-labels'].values())
            fill_holes_time = sum(times['fill-holes'].values())

            hole_filling_time = components_time + connect_labels_time + combine_labels_time + fill_holes_time

            print ('Hole Filling Time: {:0.2f} seconds'.format(hole_filling_time))
            print ('  Components Time: {:0.2f} seconds'.format(components_time))
            print ('  Connect Labels Time: {:0.2f} seconds'.format(connect_labels_time))
            print ('  Combine Labels Time: {:0.2f} seconds'.format(combine_labels_time))
            print ('  Fill Holes Time: {:0.2f} seconds'.format(fill_holes_time))

            print ()

            fd.write('Hole Filling Time: {:0.2f} seconds\n'.format(hole_filling_time))
            fd.write('Components Time: {:0.2f} seconds\n'.format(components_time))
            fd.write('Connect Labels Time: {:0.2f} seconds\n'.format(connect_labels_time))
            fd.write('Combine Labels Time: {:0.2f} seconds\n'.format(combine_labels_time))
            fd.write('Fill Holes Time: {:0.2f} seconds\n'.format(fill_holes_time))

        save_anchor_walls_time = sum(times['save-anchor-walls'].values())
        compute_anchor_points_time = sum(times['compute-anchor-points'].values())
        topological_thinning_time = sum(times['topological-thinning'].values())
        refinement_time = sum(times['skeleton-refinement'].values())

        skeletonization_time = save_anchor_walls_time + compute_anchor_points_time + topological_thinning_time + refinement_time

        print ('Skeletonization Time: {:0.2f} seconds'.format(skeletonization_time))
        print ('  Save Anchor Walls Time: {:0.2f} seconds'.format(save_anchor_walls_time))
        print ('  Compute Anchor Points Time: {:0.2f} seconds'.format(compute_anchor_points_time))
        print ('  Topological Thinning Time: {:0.2f} seconds'.format(topological_thinning_time))
        print ('  Skeleton Refinement Time: {:0.2f} seconds'.format(refinement_time))

        print ()

        fd.write('Skeletonization Time: {:0.2f} seconds\n'.format(skeletonization_time))
        fd.write('Save Anchor Walls Time: {:0.2f} seconds\n'.format(save_anchor_walls_time))
        fd.write('Compute Anchor Points Time: {:0.2f} seconds\n'.format(compute_anchor_points_time))
        fd.write('Topological Thinning Time: {:0.2f} seconds\n'.format(topological_thinning_time))
        fd.write('Skeleton Refinement Time: {:0.2f} seconds\n'.format(refinement_time))

        if not data.HoleFillingOutputDirectory() == None:
            total_time = hole_filling_time + skeletonization_time
        else:
            total_time = skeletonization_time

        print ('Total Time: {:0.2f} seconds'.format(total_time))

        print ()

        fd.write('Total Time: {:0.2f} seconds\n'.format(total_time))

    ComputeParallelStatistics(data, times)

    # open the timing filename and output per block statistics
    timing_filename = '{}/timing-statistics-per-block.pickle'.format(figures_directory)
    PickleData(times, timing_filename)



def PlotCorrelation(x, y, labels, output_prefix):
    fig, ax = plt.subplots()

    # find the correlation for these sets of points
    slope, intercept, r_value, _, _ = scipy.stats.linregress(x, y)

    # create the scatter plot
    ax.scatter(x, y, color='#328da8')

    if intercept > 0:
        best_fit_label = '$y = {:0.2f}x + {:0.2f}$ ($R^2$ = {:0.4f})'.format(slope, intercept, r_value ** 2)
    else:
        best_fit_label = '$y = {:0.2f}x - {:0.2f}$ ($R^2$ = {:0.4f})'.format(slope, -1 * intercept, r_value ** 2)


    ax.plot([0, max(x)], [intercept, slope * max(x) + intercept], color='#962020', label=best_fit_label)

    ax.set_xlabel(labels['x-label'], fontsize=14)
    ax.set_ylabel(labels['y-label'], fontsize=14)

    ax.set_title(labels['title'], fontsize=18)

    plt.legend()

    plt.tight_layout()

    output_filename = '{}.png'.format(output_prefix)
    plt.savefig(output_filename)

    # save the slope, intercept, and r_value for this configuration
    output_filename = '{}.txt'.format(output_prefix)
    with open(output_filename, 'w') as fd:
        fd.write('m = {:0.4f}\n'.format(slope))
        fd.write('b = {:0.4f}\n'.format(intercept))
        fd.write('R^2 = {:0.4f}\n'.format(r_value ** 2))

    plt.close()




def ConductBlockTimingAnalysis(meta_filenames, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    n_non_zero_voxels_per_block = {}
    n_somata_voxels_per_block = {}
    skeleton_times_per_block = {}
    hole_filling_times_per_block = {}

    for meta_filename in meta_filenames:
        print (meta_filename)

        data = ReadMetaData(meta_filename)

        # read the timing file for blocks
        figures_directory = data.FiguresDirectory()
        timing_filename = '{}/timing-statistics-per-block.pickle'.format(figures_directory)

        times = ReadPickledData(timing_filename)

        statistics_directory = '{}/statistics'.format(data.TempDirectory())

        if not data.SomataDirectory() == None:
            somata_statistics_filename = '{}/somata-statistics.pickle'.format(statistics_directory)
            somata_statistics = ReadPickledData(somata_statistics_filename)
        else:
            somata_statistics = {}

        for iz in range(data.StartZ(), data.EndZ()):
            for iy in range(data.StartY(), data.EndY()):
                for ix in range(data.StartX(), data.EndX()):
                    # read the statistics for this block
                    statistics_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pickle'.format(statistics_directory, iz, iy, ix)
                    statistics = ReadPickledData(statistics_filename)

                    # get the relevant statistics for this block
                    n_non_zero_voxels_per_block[(meta_filename, iz, iy, ix)] = statistics['filled_n_non_zero']
                    skeleton_times_per_block[(meta_filename, iz, iy, ix)] = times['skeletonization'][(iz, iy, ix)]
                    hole_filling_times_per_block[(meta_filename, iz, iy, ix)] = times['hole-filling'][(iz, iy, ix)]
                    if (iz, iy, ix) in somata_statistics:
                        n_somata_voxels_per_block[(meta_filename, iz, iy, ix)] = somata_statistics[(iz, iy, ix)]
                    else:
                        n_somata_voxels_per_block[(meta_filename, iz, iy, ix)] = 0

    # intrinsic properties of the blocks
    n_non_zero_voxels = []
    n_non_zero_voxels_sans_somata = []
    n_zero_voxels = []
    block_fill_proportion = []
    block_empty_proportion = []

    # timing properties of the blocks (seconds)
    skeleton_times = []
    hole_filling_times = []

    for key in n_non_zero_voxels_per_block.keys():
        # read the meta data to get the block size
        meta_filename = key[0]
        data = ReadMetaData(meta_filename)
        block_volume = data.BlockVolume()

        # get the intrinsic properties in list form
        n_non_zero_voxels.append(n_non_zero_voxels_per_block[key] / 10 ** 6)
        n_non_zero_voxels_sans_somata.append((n_non_zero_voxels_per_block[key] - n_somata_voxels_per_block[key]) / 10 ** 6)
        n_zero_voxels.append((block_volume - n_non_zero_voxels_per_block[key]) / 10 ** 9)

        # get the timing properties in list form (seconds)
        skeleton_times.append(skeleton_times_per_block[key])
        hole_filling_times.append(hole_filling_times_per_block[key])

    labels = {}

    output_prefix = '{}/block-based-hole-filling-time'.format(output_directory)
    labels['x-label'] = 'Billions of Background Voxels'
    labels['y-label'] = 'CPU Time (seconds)'
    labels['title'] = 'Hole Filling CPU Time'
    PlotCorrelation(n_zero_voxels, hole_filling_times, labels, output_prefix)

    output_prefix = '{}/block-based-skeleton-time'.format(output_directory)
    labels['x-label'] = 'Millions of Object Voxels'
    labels['y-label'] = 'CPU Time (seconds)'
    labels['title'] = 'Skeletonization CPU Time'
    PlotCorrelation(n_non_zero_voxels_sans_somata, skeleton_times, labels, output_prefix)

    return n_non_zero_voxels, hole_filling_times, n_non_zero_voxels_sans_somata, skeleton_times
