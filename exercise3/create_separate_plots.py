#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt
import numpy as np

def parse_output_file(filename):
    """Parse hybrid scaling output file and extract metrics"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to extract metrics - handle both × and x characters
    pattern = r"Running (\d+) Processes [×x] (\d+) Threads \((collapse|no_collapse)\).*?Max Local Computation Time \(across all ranks\): ([\d.]+)"
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    data = {
        'test1': {'collapse': {}, 'no_collapse': {}},  # Fixed 8 procs, varying threads
        'test2': {'collapse': {}, 'no_collapse': {}}   # Fixed 8 threads, varying procs
    }
    
    for procs, threads, variant, time_sec in matches:
        procs = int(procs)
        threads = int(threads)
        time_sec = float(time_sec)
        
        # Test 1: 8 processes fixed, threads varying
        if procs == 8:
            data['test1'][variant][threads] = time_sec
        
        # Test 2: 8 threads fixed, processes varying
        if threads == 8:
            data['test2'][variant][procs] = time_sec
    
    return data

def print_data_summary(data):
    """Print performance summary with runtime and speedup"""
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    
    # Test 1 Summary
    print("\nTEST 1: Fixed 8 Processes, Varying Threads")
    print("-" * 80)
    print(f"{'Threads':>8} {'Collapse Time (s)':>20} {'No-Collapse Time (s)':>20} {'Speedup':>12}")
    print("-" * 80)
    
    if data['test1']['collapse']:
        threads_list = sorted(data['test1']['collapse'].keys())
        baseline_collapse = data['test1']['collapse'][threads_list[0]]
        baseline_no_collapse = data['test1']['no_collapse'][threads_list[0]]
        
        for t in threads_list:
            time_c = data['test1']['collapse'][t]
            time_nc = data['test1']['no_collapse'][t]
            speedup = baseline_collapse / time_c
            print(f"{t:>8} {time_c:>20.4f} {time_nc:>20.4f} {speedup:>12.2f}x")
    
    # Test 2 Summary
    print("\n\nTEST 2: Fixed 8 Threads, Varying Processes")
    print("-" * 80)
    print(f"{'Processes':>8} {'Collapse Time (s)':>20} {'No-Collapse Time (s)':>20} {'Speedup':>12}")
    print("-" * 80)
    
    if data['test2']['collapse']:
        procs_list = sorted(data['test2']['collapse'].keys())
        baseline_collapse = data['test2']['collapse'][procs_list[0]]
        baseline_no_collapse = data['test2']['no_collapse'][procs_list[0]]
        
        for p in procs_list:
            time_c = data['test2']['collapse'][p]
            time_nc = data['test2']['no_collapse'][p]
            speedup = baseline_collapse / time_c
            print(f"{p:>8} {time_c:>20.4f} {time_nc:>20.4f} {speedup:>12.2f}x")
    
    print("="*80 + "\n")

def plot_test1_computation_time(data, output_file='test1_computation_time.png'):
    """Plot Test 1: 8 Processes, Varying Threads - Computation Time"""
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    threads_list = sorted(data['test1']['collapse'].keys())
    collapse_times = [data['test1']['collapse'][t] for t in threads_list]
    no_collapse_times = [data['test1']['no_collapse'][t] for t in threads_list]
    
    ax.plot(threads_list, collapse_times, 'o-', linewidth=2.5, markersize=10, label='collapse(2)', color='#1f77b4')
    ax.plot(threads_list, no_collapse_times, 's-', linewidth=2.5, markersize=10, label='no collapse', color='#ff7f0e')
    ax.set_xlabel('Number of OpenMP Threads', fontsize=13, fontweight='bold')
    ax.set_ylabel('Max Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax.set_title('Test 1: 8 MPI Processes, Varying OpenMP Threads\nComputation Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='best')
    ax.set_xticks(threads_list)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_file}")

def plot_test1_speedup(data, output_file='test1_speedup.png'):
    """Plot Test 1: 8 Processes, Varying Threads - Speedup"""
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    threads_list = sorted(data['test1']['collapse'].keys())
    collapse_times = [data['test1']['collapse'][t] for t in threads_list]
    no_collapse_times = [data['test1']['no_collapse'][t] for t in threads_list]
    
    baseline_collapse = collapse_times[0]
    baseline_no_collapse = no_collapse_times[0]
    
    speedup_collapse = [baseline_collapse / t for t in collapse_times]
    speedup_no_collapse = [baseline_no_collapse / t for t in no_collapse_times]
    
    ax.plot(threads_list, speedup_collapse, 'o-', linewidth=2.5, markersize=10, label='collapse(2)', color='#1f77b4')
    ax.plot(threads_list, speedup_no_collapse, 's-', linewidth=2.5, markersize=10, label='no collapse', color='#ff7f0e')
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('Number of OpenMP Threads', fontsize=13, fontweight='bold')
    ax.set_ylabel('Speedup (relative to baseline)', fontsize=13, fontweight='bold')
    ax.set_title('Test 1: 8 MPI Processes, Varying OpenMP Threads\nSpeedup', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='best')
    ax.set_xticks(threads_list)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_file}")

def plot_test2_computation_time(data, output_file='test2_computation_time.png'):
    """Plot Test 2: Varying Processes, 8 Threads - Computation Time"""
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    procs_list = sorted(data['test2']['collapse'].keys())
    collapse_times = [data['test2']['collapse'][p] for p in procs_list]
    no_collapse_times = [data['test2']['no_collapse'][p] for p in procs_list]
    
    ax.plot(procs_list, collapse_times, 'o-', linewidth=2.5, markersize=10, label='collapse(2)', color='#1f77b4')
    ax.plot(procs_list, no_collapse_times, 's-', linewidth=2.5, markersize=10, label='no collapse', color='#ff7f0e')
    ax.set_xlabel('Number of MPI Processes', fontsize=13, fontweight='bold')
    ax.set_ylabel('Max Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax.set_title('Test 2: Varying MPI Processes, 8 OpenMP Threads\nComputation Time', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='best')
    ax.set_xticks(procs_list)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_file}")

def plot_test2_speedup(data, output_file='test2_speedup.png'):
    """Plot Test 2: Varying Processes, 8 Threads - Speedup"""
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    procs_list = sorted(data['test2']['collapse'].keys())
    collapse_times = [data['test2']['collapse'][p] for p in procs_list]
    no_collapse_times = [data['test2']['no_collapse'][p] for p in procs_list]
    
    baseline_collapse = collapse_times[0]
    baseline_no_collapse = no_collapse_times[0]
    
    speedup_collapse = [baseline_collapse / t for t in collapse_times]
    speedup_no_collapse = [baseline_no_collapse / t for t in no_collapse_times]
    
    ax.plot(procs_list, speedup_collapse, 'o-', linewidth=2.5, markersize=10, label='collapse(2)', color='#1f77b4')
    ax.plot(procs_list, speedup_no_collapse, 's-', linewidth=2.5, markersize=10, label='no collapse', color='#ff7f0e')
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('Number of MPI Processes', fontsize=13, fontweight='bold')
    ax.set_ylabel('Speedup (relative to baseline)', fontsize=13, fontweight='bold')
    ax.set_title('Test 2: Varying MPI Processes, 8 OpenMP Threads\nSpeedup', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='best')
    ax.set_xticks(procs_list)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = 'hybrid_scaling_perf_24039061.out'
    
    print(f"Parsing {output_file}...")
    data = parse_output_file(output_file)
    
    # Print performance summary
    print_data_summary(data)
    
    # Create four separate plots
    if data['test1']['collapse']:
        plot_test1_computation_time(data)
        plot_test1_speedup(data)
    else:
        print("Warning: No Test 1 data found")
    
    if data['test2']['collapse']:
        plot_test2_computation_time(data)
        plot_test2_speedup(data)
    else:
        print("Warning: No Test 2 data found")
    
    print("\nAll plots generated successfully!")

