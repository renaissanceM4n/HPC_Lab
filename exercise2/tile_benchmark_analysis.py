#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def parse_tile_benchmark_output(filename):
    """
    Parse tile_benchmark_*.out file and extract timing data.
    Returns a dict with structure:
    {tile_size: {num_processes: max_time}}
    """
    data = defaultdict(dict)
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    current_tile_size = None
    current_processes = None
    
    for line in lines:
        # Match tile size line: "=== Testing Tile Size: 32x32 ==="
        tile_match = re.search(r'Testing Tile Size:\s*(\d+)x\d+', line)
        if tile_match:
            current_tile_size = int(tile_match.group(1))
            continue
        
        # Match process count line: "Running test with tile size ... at 24 processes..."
        proc_match = re.search(r'at (\d+) processes', line)
        if proc_match:
            current_processes = int(proc_match.group(1))
            continue
        
        # Match max time line: "Max Local Computation Time (across all ranks): 15.234 seconds"
        time_match = re.search(r'Max Local Computation Time.*?:\s*([\d.]+)\s*seconds', line)
        if time_match and current_tile_size is not None and current_processes is not None:
            max_time = float(time_match.group(1))
            data[current_tile_size][current_processes] = max_time
    
    return data

def calculate_speedup(data, reference_processes=20):
    """
    Calculate speedup relative to reference process count.
    Returns a dict with structure:
    {tile_size: {num_processes: speedup}}
    """
    speedup_data = defaultdict(dict)
    
    for tile_size, processes_dict in data.items():
        if reference_processes in processes_dict:
            reference_time = processes_dict[reference_processes]
            for num_procs, time_val in processes_dict.items():
                speedup_data[tile_size][num_procs] = reference_time / time_val
        else:
            print(f"Warning: Reference process count {reference_processes} not found for tile size {tile_size}")
    
    return speedup_data

def plot_tile_comparison(data, output_filename='tile_size_speedup.png'):
    """
    Plot speedup comparison for different tile sizes (similar to strong_scaling.py).
    """
    # Sort tile sizes for consistent ordering
    tile_sizes = sorted(data.keys())
    colors = plt.cm.tab10(np.linspace(0, 1, len(tile_sizes)))
    
    # Extract process counts
    all_processes = set()
    for tile_size_data in data.values():
        all_processes.update(tile_size_data.keys())
    process_counts = sorted(all_processes)
    
    # Calculate speedup data
    speedup_data = calculate_speedup(data, reference_processes=20)
    
    # Plot
    plt.figure(figsize=(10, 6))
    
    # Plot speedup for each tile size
    for tile_size, color in zip(tile_sizes, colors):
        speedups = [speedup_data[tile_size].get(p, None) for p in process_counts]
        valid_speedups = [(p, s) for p, s in zip(process_counts, speedups) if s is not None]
        if valid_speedups:
            procs, speedups_valid = zip(*valid_speedups)
            plt.plot(procs, speedups_valid, 'o-', color=color, linewidth=2, markersize=6,
                    label=f'Tile {tile_size}x{tile_size}')
    
    # Add ideal speedup line
    plt.plot(process_counts, [p/20 for p in process_counts], 'k--', linewidth=2, 
            label='Ideal Speedup', alpha=0.5)
    
    plt.xlabel('Number of Processes', fontsize=12, fontweight='bold')
    plt.ylabel('Speedup (relative to 20 processes)', fontsize=12, fontweight='bold')
    plt.title('Tile Size Benchmark: Speedup Comparison', fontsize=13, fontweight='bold')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend(fontsize=10, loc='best')
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print(f"✓ Plot saved to {output_filename}")
    plt.close()

def print_summary_table(data):
    """
    Print a summary table of runtimes.
    """
    tile_sizes = sorted(data.keys())
    all_processes = set()
    for tile_size_data in data.values():
        all_processes.update(tile_size_data.keys())
    process_counts = sorted(all_processes)
    
    print("\n" + "="*80)
    print("RUNTIME SUMMARY (Max Computation Time in seconds)")
    print("="*80)
    
    # Header
    print(f"{'Tile Size':<15}", end="")
    for p in process_counts:
        print(f"{p:>10}p", end="")
    print()
    print("-" * (15 + 11 * len(process_counts)))
    
    # Data rows
    for tile_size in tile_sizes:
        print(f"{tile_size:>2}x{tile_size:<10}", end="")
        for p in process_counts:
            if p in data[tile_size]:
                print(f"{data[tile_size][p]:>10.2f}", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()
    
    print("\n" + "="*80)
    print("SPEEDUP SUMMARY (relative to 20 processes)")
    print("="*80)
    
    speedup_data = calculate_speedup(data, reference_processes=20)
    
    # Header
    print(f"{'Tile Size':<15}", end="")
    for p in process_counts:
        print(f"{p:>10}p", end="")
    print()
    print("-" * (15 + 11 * len(process_counts)))
    
    # Data rows
    for tile_size in tile_sizes:
        print(f"{tile_size:>2}x{tile_size:<10}", end="")
        for p in process_counts:
            if p in speedup_data[tile_size]:
                print(f"{speedup_data[tile_size][p]:>10.2f}x", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()
    
    print()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tile_benchmark_analysis.py <tile_benchmark_output_file> [output_plot_name]")
        print("\nExample: python tile_benchmark_analysis.py tile_benchmark_12345.out")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_plot = sys.argv[2] if len(sys.argv) > 2 else 'tile_size_comparison.png'
    
    print(f"Parsing {input_file}...")
    data = parse_tile_benchmark_output(input_file)
    
    if not data:
        print("Error: No data found in file. Please check the file format.")
        sys.exit(1)
    
    print(f"Found {len(data)} tile sizes")
    for tile_size in sorted(data.keys()):
        print(f"  Tile {tile_size}x{tile_size}: {len(data[tile_size])} process counts")
    
    # Print summary tables
    print_summary_table(data)
    
    # Generate plot
    plot_tile_comparison(data, output_plot)

if __name__ == "__main__":
    main()
