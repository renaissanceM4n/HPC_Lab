#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt
import numpy as np

def parse_output_file(filename):
    """Parse hybrid scaling output file and extract metrics"""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Pattern to extract metrics (Max instead of Avg)
    pattern = r"Running (\d+) Processes × (\d+) Threads \((collapse|no_collapse)\).*?Max Local Computation Time \(across all ranks\): ([\d.]+) seconds"
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    data = {
        'test1': {'collapse': {}, 'no_collapse': {}},  # Fixed 4 procs, varying threads
        'test2': {'collapse': {}, 'no_collapse': {}}   # Fixed 4 threads, varying procs
    }
    
    for procs, threads, variant, time_sec in matches:
        procs = int(procs)
        threads = int(threads)
        time_sec = float(time_sec)
        
        # Test 1: 4 processes fixed, threads varying
        if procs == 4:
            data['test1'][variant][threads] = time_sec
        
        # Test 2: 4 threads fixed, processes varying
        if threads == 4:
            data['test2'][variant][procs] = time_sec
    
    return data

def plot_results(data, output_file='hybrid_scaling_plots.png'):
    """Create two subplots for the scaling results with Speedup"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Test 1: Fixed 4 Processes, Varying Threads
    threads_list = sorted(data['test1']['collapse'].keys())
    collapse_times_1 = [data['test1']['collapse'][t] for t in threads_list]
    no_collapse_times_1 = [data['test1']['no_collapse'][t] for t in threads_list]
    
    # Plot computation times (top left)
    ax1.plot(threads_list, collapse_times_1, 'o-', linewidth=2, markersize=8, label='collapse', color='#1f77b4')
    ax1.plot(threads_list, no_collapse_times_1, 's-', linewidth=2, markersize=8, label='no_collapse', color='#ff7f0e')
    ax1.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Max Computation Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Test 1: 4 Processes, Varying Threads\nMax Computation Time (Single NUMA Domain)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    ax1.set_xticks(threads_list)
    
    # Calculate and plot speedup (bottom left)
    baseline_collapse_1 = collapse_times_1[0]  # 4 threads as baseline
    baseline_no_collapse_1 = no_collapse_times_1[0]
    
    speedup_collapse_1 = [baseline_collapse_1 / t for t in collapse_times_1]
    speedup_no_collapse_1 = [baseline_no_collapse_1 / t for t in no_collapse_times_1]
    
    ax3.plot(threads_list, speedup_collapse_1, 'o-', linewidth=2, markersize=8, label='collapse', color='#1f77b4')
    ax3.plot(threads_list, speedup_no_collapse_1, 's-', linewidth=2, markersize=8, label='no_collapse', color='#ff7f0e')
    ax3.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax3.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Speedup (relative to 4 Threads)', fontsize=12, fontweight='bold')
    ax3.set_title('Test 1: 4 Processes, Varying Threads\nSpeedup', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=11)
    ax3.set_xticks(threads_list)
    
    # Test 2: Fixed 4 Threads, Varying Processes
    procs_list = sorted(data['test2']['collapse'].keys())
    collapse_times_2 = [data['test2']['collapse'][p] for p in procs_list]
    no_collapse_times_2 = [data['test2']['no_collapse'][p] for p in procs_list]
    
    # Plot computation times (top right)
    ax2.plot(procs_list, collapse_times_2, 'o-', linewidth=2, markersize=8, label='collapse', color='#1f77b4')
    ax2.plot(procs_list, no_collapse_times_2, 's-', linewidth=2, markersize=8, label='no_collapse', color='#ff7f0e')
    ax2.set_xlabel('Number of Processes', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Max Computation Time (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Test 2: 4 Threads, Varying Processes\nMax Computation Time (Single NUMA Domain)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    ax2.set_xticks(procs_list)
    
    # Calculate and plot speedup (bottom right)
    baseline_collapse_2 = collapse_times_2[0]  # 4 processes as baseline
    baseline_no_collapse_2 = no_collapse_times_2[0]
    
    speedup_collapse_2 = [baseline_collapse_2 / t for t in collapse_times_2]
    speedup_no_collapse_2 = [baseline_no_collapse_2 / t for t in no_collapse_times_2]
    
    ax4.plot(procs_list, speedup_collapse_2, 'o-', linewidth=2, markersize=8, label='collapse', color='#1f77b4')
    ax4.plot(procs_list, speedup_no_collapse_2, 's-', linewidth=2, markersize=8, label='no_collapse', color='#ff7f0e')
    ax4.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax4.set_xlabel('Number of Processes', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Speedup (relative to 4 Processes)', fontsize=12, fontweight='bold')
    ax4.set_title('Test 2: 4 Threads, Varying Processes\nSpeedup', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=11)
    ax4.set_xticks(procs_list)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_file}")
    plt.show()

def print_data_summary(data):
    """Print summary of parsed data"""
    
    print("\n" + "="*60)
    print("TEST 1: Fixed 4 Processes, Varying Threads")
    print("="*60)
    print(f"{'Threads':<10} {'collapse (s)':<20} {'no_collapse (s)':<20}")
    print("-"*60)
    for threads in sorted(data['test1']['collapse'].keys()):
        c_time = data['test1']['collapse'][threads]
        nc_time = data['test1']['no_collapse'][threads]
        print(f"{threads:<10} {c_time:<20.4f} {nc_time:<20.4f}")
    
    print("\n" + "="*60)
    print("TEST 2: Fixed 4 Threads, Varying Processes")
    print("="*60)
    print(f"{'Processes':<10} {'collapse (s)':<20} {'no_collapse (s)':<20}")
    print("-"*60)
    for procs in sorted(data['test2']['collapse'].keys()):
        c_time = data['test2']['collapse'][procs]
        nc_time = data['test2']['no_collapse'][procs]
        print(f"{procs:<10} {c_time:<20.4f} {nc_time:<20.4f}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = 'hybrid_scaling_24037381.out'
    
    print(f"Parsing {output_file}...")
    data = parse_output_file(output_file)
    
    print_data_summary(data)
    plot_results(data)
