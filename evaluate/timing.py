import os
import statistics



import numpy as np



import matplotlib
from matplotlib import pyplot as plt

# set matplotlib styles
plt.style.use('seaborn-white')



from blockbased_synapseaware.utilities.dataIO import ReadMetaData, ReadPickledData



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
    total_times = []

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
                    total_times.append(ParseLine(rfd.readline()))

    print ('Connected Components')
    wfd.write('Connected Components\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Components Time', components_times, wfd)
    PrintStatistics('Adjacency Set Time', adjacency_set_times, wfd)
    PrintStatistics('Background Components Associated Labels Time', background_components_associated_labels_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

    return total_times



def ConnectLabelsAcrossBlocks(data, wfd):
    timing_directory = '{}/connect-labels-across-blocks'.format(data.TimingDirectory())

    adjacency_set_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    adjacency_set_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times.append(ParseLine(rfd.readline()))

    print ('Connect Labels Across Blocks')
    wfd.write('Connect Labels Across Blocks\n')

    PrintStatistics('Adjacency Set Time', adjacency_set_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

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

    return [total_time]



def FillHoles(data, wfd):
    timing_directory = '{}/fill-holes'.format(data.TimingDirectory())

    read_times = []
    hole_fill_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    hole_fill_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times.append(ParseLine(rfd.readline()))

    print ('Fill Holes')
    wfd.write('Fill Holes\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Hole Fill Time', hole_fill_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

    return total_times



def SaveAnchorWalls(data, wfd):
    timing_directory = '{}/save-anchor-walls'.format(data.TimingDirectory())

    read_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    write_times.append(ParseLine(rfd.readline()))
                    total_times.append(ParseLine(rfd.readline()))

    print ('Save Anchor Walls')
    wfd.write('Save Anchor Walls\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Write Time', write_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

    return total_times



def ComputeAnchorPoints(data, wfd):
    timing_directory = '{}/compute-anchor-points'.format(data.TimingDirectory())

    z_anchor_computation_times = []
    y_anchor_computation_times = []
    x_anchor_computation_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    z_anchor_computation_times.append(ParseLine(rfd.readline()))
                    y_anchor_computation_times.append(ParseLine(rfd.readline()))
                    x_anchor_computation_times.append(ParseLine(rfd.readline()))
                    total_times.append(ParseLine(rfd.readline()))

    print ('Compute Anchor Points')
    wfd.write('Compute Anchor Points\n')

    PrintStatistics('Z Anchor Computation Time', z_anchor_computation_times, wfd)
    PrintStatistics('Y Anchor Computation Time', y_anchor_computation_times, wfd)
    PrintStatistics('X Anchor Computation Time', x_anchor_computation_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

    return total_times



def TopologicalThinning(data, wfd):
    timing_directory = '{}/topological-thinning'.format(data.TimingDirectory())

    read_times = []
    thinning_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as rfd:
                    read_times.append(ParseLine(rfd.readline()))
                    thinning_times.append(ParseLine(rfd.readline()))
                    total_times.append(ParseLine(rfd.readline()))

    print ('Topological Thinning')
    wfd.write('Topological Thinning\n')

    PrintStatistics('Read Time', read_times, wfd)
    PrintStatistics('Thinning Time', thinning_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

    return total_times



def SkeletonRefinement(data, wfd):
    timing_directory = '{}/skeleton-refinement'.format(data.TimingDirectory())

    refinement_times = []
    updated_widths_times = []
    total_times = []

    for label in range(1, data.NLabels()):
        timing_filename = '{}/{:016d}.txt'.format(timing_directory, label)
        if not os.path.exists(timing_filename): continue

        with open(timing_filename, 'r') as rfd:
            refinement_times.append(ParseLine(rfd.readline()))
            updated_widths_times.append(ParseLine(rfd.readline()))
            total_times.append(ParseLine(rfd.readline()))

    print ('Skeleton Refinement')
    wfd.write('Skeleton Refinement\n')

    PrintStatistics('Refinement Time', refinement_times, wfd)
    PrintStatistics('Update Widths Time', updated_widths_times, wfd)
    PrintStatistics('Total Time', total_times, wfd)

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
            for time in times[task]:
                jobs.append(time)
        elif strategy == 'LPT':
            for time in sorted(times[task], reverse=True):
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

    cpus = [cpu for cpu in range(1, nblocks, nblocks // 10)]
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

    # skeleton generation
    times['save-anchor-walls'] = SaveAnchorWalls(data, fd)
    times['compute-anchor-points'] = ComputeAnchorPoints(data, fd)
    times['topological-thinning'] = TopologicalThinning(data, fd)
    times['skeleton-refinement'] = SkeletonRefinement(data, fd)

    # close the timing file
    fd.close()

    ComputeParallelStatistics(data, times)
    #ConductBlockTimingAnalysis(data, times)
