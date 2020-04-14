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



def PrintStatistics(title, times):
    avg = statistics.mean(times)
    stddev = statistics.stdev(times)

    print ('  {:45s} {:10.2f} seconds (\u00B1{:0.2f})'.format(title, avg, stddev))



def ConnectedComponents(data):
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

                with open(timing_filename, 'r') as fd:
                    read_times.append(ParseLine(fd.readline()))
                    components_times.append(ParseLine(fd.readline()))
                    adjacency_set_times.append(ParseLine(fd.readline()))
                    background_components_associated_labels_times.append(ParseLine(fd.readline()))
                    write_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Connected Components')
    PrintStatistics('Read Time', read_times)
    PrintStatistics('Components Time', components_times)
    PrintStatistics('Adjacency Set Time', adjacency_set_times)
    PrintStatistics('Background Components Associated Labels Time', background_components_associated_labels_times)
    PrintStatistics('Write Time', write_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def ConnectLabelsAcrossBlocks(data):
    timing_directory = '{}/connect-labels-across-blocks'.format(data.TimingDirectory())

    adjacency_set_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as fd:
                    adjacency_set_times.append(ParseLine(fd.readline()))
                    write_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Connect Labels Across Blocks')
    PrintStatistics('Adjacency Set Time', adjacency_set_times)
    PrintStatistics('Write Time', write_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def CombineAssociatedLabels(data):
    timing_directory = data.TimingDirectory()

    timing_filename = '{}/combine-associated-labels.txt'.format(timing_directory)

    with open(timing_filename, 'r') as fd:
        read_time = ParseLine(fd.readline())
        adjacency_set_time = ParseLine(fd.readline())
        write_time = ParseLine(fd.readline())
        total_time = ParseLine(fd.readline())

    print ('Combine Associated Labels')
    print ('  {:45s} {:10.2f} seconds'.format('Read Time', read_time))
    print ('  {:45s} {:10.2f} seconds'.format('Adjacency Set Time', adjacency_set_time))
    print ('  {:45s} {:10.2f} seconds'.format('Write Time', write_time))
    print ('  {:45s} {:10.2f} seconds'.format('Total Time', total_time))

    return [total_time]



def FillHoles(data):
    timing_directory = '{}/fill-holes'.format(data.TimingDirectory())

    read_times = []
    hole_fill_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as fd:
                    read_times.append(ParseLine(fd.readline()))
                    hole_fill_times.append(ParseLine(fd.readline()))
                    write_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Fill Holes')
    PrintStatistics('Read Time', read_times)
    PrintStatistics('Hole Fill Time', hole_fill_times)
    PrintStatistics('Write Time', write_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def SaveAnchorWalls(data):
    timing_directory = '{}/save-anchor-walls'.format(data.TimingDirectory())

    read_times = []
    write_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as fd:
                    read_times.append(ParseLine(fd.readline()))
                    write_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Save Anchor Walls')
    PrintStatistics('Read Time', read_times)
    PrintStatistics('Write Time', write_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def ComputeAnchorPoints(data):
    timing_directory = '{}/compute-anchor-points'.format(data.TimingDirectory())

    z_anchor_computation_times = []
    y_anchor_computation_times = []
    x_anchor_computation_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as fd:
                    z_anchor_computation_times.append(ParseLine(fd.readline()))
                    y_anchor_computation_times.append(ParseLine(fd.readline()))
                    x_anchor_computation_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Compute Anchor Points')
    PrintStatistics('Z Anchor Computation Time', z_anchor_computation_times)
    PrintStatistics('Y Anchor Computation Time', y_anchor_computation_times)
    PrintStatistics('X Anchor Computation Time', x_anchor_computation_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def TopologicalThinning(data):
    timing_directory = '{}/topological-thinning'.format(data.TimingDirectory())

    read_times = []
    thinning_times = []
    total_times = []

    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                timing_filename = '{}/{:04d}z-{:04d}y-{:04d}x.txt'.format(timing_directory, iz, iy, ix)

                with open(timing_filename, 'r') as fd:
                    read_times.append(ParseLine(fd.readline()))
                    thinning_times.append(ParseLine(fd.readline()))
                    total_times.append(ParseLine(fd.readline()))

    print ('Topological Thinning')
    PrintStatistics('Read Time', read_times)
    PrintStatistics('Thinning Time', thinning_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def SkeletonRefinement(data):
    timing_directory = '{}/skeleton-refinement'.format(data.TimingDirectory())

    refinement_times = []
    updated_widths_times = []
    total_times = []

    for label in range(1, data.NLabels()):
        timing_filename = '{}/{:016d}.txt'.format(timing_directory, label)
        if not os.path.exists(timing_filename): continue

        with open(timing_filename, 'r') as fd:
            refinement_times.append(ParseLine(fd.readline()))
            updated_widths_times.append(ParseLine(fd.readline()))
            total_times.append(ParseLine(fd.readline()))

    print ('Skeleton Refinement')
    PrintStatistics('Refinement Time', refinement_times)
    PrintStatistics('Update Widths Time', updated_widths_times)
    PrintStatistics('Total Time', total_times)

    return total_times



def LPT(jobs, m_cpus):
    # create empty cpus
    cpu_times = np.zeros(m_cpus, dtype=np.float32)

    # sort the jobs in descending running time
    # do not use in-place sorting since times must remain sorted elsewhere
    sorted_jobs = sorted(jobs, reverse = True)

    for job in sorted_jobs:
        estimated_best_cpu = np.argmin(cpu_times)

        cpu_times[estimated_best_cpu] += job

    clock_time = max(cpu_times)
    idle_time = (m_cpus * clock_time) - sum(cpu_times)

    return clock_time, idle_time



def PlotClockAndIdleTime(data, clock_times, idle_times, output_filename):
    fig, ax1 = plt.subplots()

    max_cpus = len(clock_times) + 1
    cpus = range(1, max_cpus)

    ax1.set_xlabel('No. CPUs')
    ax1.set_ylabel('Total Clock Time (s)')
    ax1.plot(cpus, clock_times)

    ax1.set_xlim(1, max_cpus)

    ax2 = ax1.twinx()
    ax2.set_ylabel('CPU Time Idle (%)')
    ax2.plot(cpus, idle_times, color='r')

    # get the output filename for this block
    figures_directory = data.FiguresDirectory()
    if not os.path.exists(figures_directory):
        os.makedirs(figures_directory, exist_ok=True)

    output_filename = '{}/{}'.format(figures_directory, output_filename)

    # show the figure
    plt.savefig(output_filename)



def ComputeParallelStatistics(data, times):
    # find the most cpus that could be useful (most jobs in one step)
    maximum_cpus = 0
    for step in times.keys():
        maximum_cpus = max(maximum_cpus, len(times[step]))

    total_clock_times = []
    total_idle_times = []

    # calculate the optimal amount of time with this many CPUs
    for cpu in range(1, maximum_cpus + 1):

        # the clock time and idle time for this number of cpus
        total_clock_time = 0
        total_idle_time = 0

        for step in times.keys():
            # estimate the optimal time using the Longest Processing Time (LPT) heuristic
            # achieves an upper bound of 4/3 - 1 / (3m) the optimal time
            lpt_clock_time, lpt_idle_time = LPT(times[step], cpu)

            # update the total clock and idle time after this step
            total_clock_time += lpt_clock_time
            total_idle_time += lpt_idle_time

        total_clock_times.append(total_clock_time)
        total_idle_times.append(total_idle_time)

    PlotClockAndIdleTime(data, total_clock_times, total_idle_times, 'cpu-usage.png')



def GenerateBlockTimingPlot(data, description, n_non_zero_voxels, times, output_filename):
    fig, ax = plt.subplots()

    # set the title and labels
    ax.set_title('{} {}'.format(data.prefix, description), fontsize=14)
    ax.set_ylabel('CPU Time (s)', fontsize=10)
    ax.set_xlabel('No. Non Zero Voxels (Millions)', fontsize=10)

    # show a scatter plot of voxels and times
    ax.scatter(n_non_zero_voxels, times)

    fig.tight_layout()

    # get the output filename for this block
    figures_directory = data.FiguresDirectory()
    if not os.path.exists(figures_directory):
        os.makedirs(figures_directory, exist_ok=True)

    output_filename = '{}/{}'.format(figures_directory, output_filename)

    # show the figure
    plt.savefig(output_filename)



def ConductBlockTimingAnalysis(data, times):
    # directory that contains
    statistics_directory = '{}/statistics'.format(data.TempDirectory())

    # create empty arrays for the block timing analysis
    component_times = []
    connect_labels_times = []
    fill_holes_times = []
    save_anchor_walls_times = []
    compute_anchor_points_times = []
    topological_thinning_times = []

    # create aggregate variables
    hole_filling_times = []
    skeletonize_times = []
    total_times = []

    n_non_zero_voxels = []

    # iterate over every block
    index = 0 # counter to return the total time for each block
    for iz in range(data.StartZ(), data.EndZ()):
        for iy in range(data.StartY(), data.EndY()):
            for ix in range(data.StartX(), data.EndX()):
                statistics_filename = '{}/{:04d}z-{:04d}y-{:04d}x.pickle'.format(statistics_directory, iz, iy, ix)
                statistics = ReadPickledData(statistics_filename)

                # get the the number of non zero voxels in this block (in millions)
                n_non_zero_voxels.append(statistics['filled_n_non_zero'] / million)

                # get the time for each step
                component_times.append(times['components'][index])
                connect_labels_times.append(times['connect-labels'][index])
                fill_holes_times.append(times['fill-holes'][index])
                save_anchor_walls_times.append(times['save-anchor-walls'][index])
                compute_anchor_points_times.append(times['compute-anchor-points'][index])
                topological_thinning_times.append(times['topological-thinning'][index])

                hole_filling_times.append(component_times[-1] + connect_labels_times[-1] + fill_holes_times[-1])
                skeletonize_times.append(save_anchor_walls_times[-1] + compute_anchor_points_times[-1] + topological_thinning_times[-1])
                total_times.append(hole_filling_times[-1] + skeletonize_times[-1])

                index += 1

    GenerateBlockTimingPlot(data, 'Hole Filling Time', n_non_zero_voxels, hole_filling_times, 'hole-filling-time.png')
    GenerateBlockTimingPlot(data, 'Skeleton Generation Time', n_non_zero_voxels, skeletonize_times, 'skeleton-generation-time.png')
    GenerateBlockTimingPlot(data, 'Total Running Time', n_non_zero_voxels, total_times, 'total-running-time.png')



def ConductEndToEndTimingAnalysis(prefix):
    # run analysis for this dataset
    data = ReadMetaData(prefix)

    assert (not data.FiguresDirectory() == None)

    # collect the timing statistics for all blocks
    times = {}

    # hole filling
    times['components'] = ConnectedComponents(data)
    times['connect-labels'] = ConnectLabelsAcrossBlocks(data)
    times['combine-labels'] = CombineAssociatedLabels(data)
    times['fill-holes'] = FillHoles(data)

    # skeleton generation
    times['save-anchor-walls'] = SaveAnchorWalls(data)
    times['compute-anchor-points'] = ComputeAnchorPoints(data)
    times['topological-thinning'] = TopologicalThinning(data)
    times['skeleton-refinement'] = SkeletonRefinement(data)

    ComputeParallelStatistics(data, times)
    ConductBlockTimingAnalysis(data, times)
