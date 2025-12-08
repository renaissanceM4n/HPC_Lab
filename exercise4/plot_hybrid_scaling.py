#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import sys

def parse_hybrid_scaling_output(filename):
    """
    Parse hybrid_scaling_*.out file and extract timing data.
    Returns a dict with structure:
    {tile_size: {(processes, threads): max_time}}
    """
    data = defaultdict(lambda: defaultdict(float))
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find all tile size blocks
    tile_pattern = r'TILE SIZE:\s*(\d+)x\d+.*?(?=TILE SIZE:|Hybrid scaling tests completed)'
    
    for tile_match in re.finditer(tile_pattern, content, re.DOTALL):
        tile_size = int(tile_match.group(1))
        tile_block = tile_match.group(0)
        
        # Find all configuration blocks within this tile
        config_pattern = r'Configuration:\s*(\d+)\s*Processes\s*×\s*(\d+)\s*Threads.*?Max Local Computation Time.*?:\s*([\d.]+)\s*seconds'
        
        for config_match in re.finditer(config_pattern, tile_block, re.DOTALL):
            procs = int(config_match.group(1))
            threads = int(config_match.group(2))
            max_time = float(config_match.group(3))
            
            data[tile_size][(procs, threads)] = max_time
    
    return data

def create_scaling_plots(data, output_dir='results'):
    """
    Create plots showing scaling behavior for each tile size.
    """
    tile_sizes = sorted(data.keys())
    
    # For each tile size, create scaling plots
    for tile_size in tile_sizes:
        configs = data[tile_size]
        
        # Separate Phase 1 (fixed procs=4, varying threads) and Phase 2 (fixed threads=4, varying procs)
        phase1_data = {}  # threads -> time
        phase2_data = {}  # procs -> time
        
        for (procs, threads), time_val in configs.items():
            if procs == 4:
                phase1_data[threads] = time_val
            if threads == 4:
                phase2_data[procs] = time_val
        
        # Create combined plot for this tile size
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Phase 1: Fixed 4 Processes, Scaling Threads
        if phase1_data:
            threads_vals = sorted(phase1_data.keys())
            times1 = [phase1_data[t] for t in threads_vals]
            
            ax1.plot(threads_vals, times1, 'o-', color='#2E86AB', linewidth=2.5, markersize=8, label='Execution Time')
            ax1.fill_between(threads_vals, times1, alpha=0.3, color='#2E86AB')
            
            # Add value labels
            for t, time_val in zip(threads_vals, times1):
                ax1.text(t, time_val, f'{time_val:.1f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax1.set_xlabel('Number of Threads (fixed 4 processes)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
            ax1.set_title(f'Phase 1: Tile {tile_size}×{tile_size} - Thread Scaling\n(4 Processes × Threads)', fontsize=12, fontweight='bold')
            ax1.set_xticks(threads_vals)
            ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
            ax1.legend(fontsize=10)
        
        # Phase 2: Fixed 4 Threads, Scaling Processes
        if phase2_data:
            procs_vals = sorted(phase2_data.keys())
            times2 = [phase2_data[p] for p in procs_vals]
            
            ax2.plot(procs_vals, times2, 's-', color='#A23B72', linewidth=2.5, markersize=8, label='Execution Time')
            ax2.fill_between(procs_vals, times2, alpha=0.3, color='#A23B72')
            
            # Add value labels
            for p, time_val in zip(procs_vals, times2):
                ax2.text(p, time_val, f'{time_val:.1f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax2.set_xlabel('Number of Processes (fixed 4 threads)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
            ax2.set_title(f'Phase 2: Tile {tile_size}×{tile_size} - Process Scaling\n(Processes × 4 Threads)', fontsize=12, fontweight='bold')
            ax2.set_xticks(procs_vals)
            ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
            ax2.legend(fontsize=10)
        
        plt.tight_layout()
        filename = f'{output_dir}/hybrid_scaling_tile_{tile_size}x{tile_size}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()

def create_comparison_plot(data, output_dir='results'):
    """
    Create a comparison plot showing all tile sizes side by side.
    """
    tile_sizes = sorted(data.keys())
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(tile_sizes)))
    color_map = {size: colors[i] for i, size in enumerate(tile_sizes)}
    
    # Phase 1: Fixed 4 Processes, Scaling Threads
    ax1 = axes[0]
    for tile_size in tile_sizes:
        configs = data[tile_size]
        phase1_data = {}
        
        for (procs, threads), time_val in configs.items():
            if procs == 4:
                phase1_data[threads] = time_val
        
        if phase1_data:
            threads_vals = sorted(phase1_data.keys())
            times = [phase1_data[t] for t in threads_vals]
            ax1.plot(threads_vals, times, 'o-', color=color_map[tile_size], linewidth=2, markersize=6,
                    label=f'Tile {tile_size}×{tile_size}')
    
    ax1.set_xlabel('Number of Threads (fixed 4 processes)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax1.set_title('Phase 1: Thread Scaling Comparison (4 Processes)', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.legend(fontsize=10)
    
    # Get all unique thread values for x-axis
    all_threads = set()
    for tile_size in tile_sizes:
        for (procs, threads), _ in data[tile_size].items():
            if procs == 4:
                all_threads.add(threads)
    if all_threads:
        ax1.set_xticks(sorted(all_threads))
    
    # Phase 2: Fixed 4 Threads, Scaling Processes
    ax2 = axes[1]
    for tile_size in tile_sizes:
        configs = data[tile_size]
        phase2_data = {}
        
        for (procs, threads), time_val in configs.items():
            if threads == 4:
                phase2_data[procs] = time_val
        
        if phase2_data:
            procs_vals = sorted(phase2_data.keys())
            times = [phase2_data[p] for p in procs_vals]
            ax2.plot(procs_vals, times, 's-', color=color_map[tile_size], linewidth=2, markersize=6,
                    label=f'Tile {tile_size}×{tile_size}')
    
    ax2.set_xlabel('Number of Processes (fixed 4 threads)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Execution Time (seconds)', fontsize=11, fontweight='bold')
    ax2.set_title('Phase 2: Process Scaling Comparison (4 Threads)', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.legend(fontsize=10)
    
    # Get all unique process values for x-axis
    all_procs = set()
    for tile_size in tile_sizes:
        for (procs, threads), _ in data[tile_size].items():
            if threads == 4:
                all_procs.add(procs)
    if all_procs:
        ax2.set_xticks(sorted(all_procs))
    plt.tight_layout()
    filename = f'{output_dir}/hybrid_scaling_comparison.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved: {filename}")
    plt.close()

def create_speedup_plot(data, output_dir='results'):
    """
    Create speedup plots relative to baseline (4p×4t).
    """
    tile_sizes = sorted(data.keys())
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(tile_sizes)))
    color_map = {size: colors[i] for i, size in enumerate(tile_sizes)}
    
    # Phase 1: Fixed 4 Processes, Scaling Threads
    ax1 = axes[0]
    for tile_size in tile_sizes:
        configs = data[tile_size]
        baseline_time = configs.get((4, 4), None)
        
        if baseline_time:
            phase1_data = {}
            for (procs, threads), time_val in configs.items():
                if procs == 4:
                    phase1_data[threads] = baseline_time / time_val  # speedup
            
            if phase1_data:
                threads_vals = sorted(phase1_data.keys())
                speedups = [phase1_data[t] for t in threads_vals]
                ax1.plot(threads_vals, speedups, 'o-', color=color_map[tile_size], linewidth=2, markersize=6,
                        label=f'Tile {tile_size}×{tile_size}')
    
    # Add ideal line
    all_threads = set()
    for tile_size in tile_sizes:
        for (procs, threads), _ in data[tile_size].items():
            if procs == 4:
                all_threads.add(threads)
    
    ax1.set_xlabel('Number of Threads', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Speedup (relative to 4 threads)', fontsize=11, fontweight='bold')
    ax1.set_title('Phase 1: Thread Speedup Comparison', fontsize=12, fontweight='bold')
    ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.legend(fontsize=10)
    
    if all_threads:
        ax1.set_xticks(sorted(all_threads))
    
    # Phase 2: Fixed 4 Threads, Scaling Processes
    ax2 = axes[1]
    for tile_size in tile_sizes:
        configs = data[tile_size]
        baseline_time = configs.get((4, 4), None)
        
        if baseline_time:
            phase2_data = {}
            for (procs, threads), time_val in configs.items():
                if threads == 4:
                    phase2_data[procs] = baseline_time / time_val  # speedup
            
            if phase2_data:
                procs_vals = sorted(phase2_data.keys())
                speedups = [phase2_data[p] for p in procs_vals]
                ax2.plot(procs_vals, speedups, 's-', color=color_map[tile_size], linewidth=2, markersize=6,
                        label=f'Tile {tile_size}×{tile_size}')
    
    # Get all unique process values for x-axis
    all_procs = set()
    for tile_size in tile_sizes:
        for (procs, threads), _ in data[tile_size].items():
            if threads == 4:
                all_procs.add(procs)
    
    ax2.set_xlabel('Number of Processes', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Speedup (relative to 4 processes)', fontsize=11, fontweight='bold')
    ax2.set_title('Phase 2: Process Speedup Comparison', fontsize=12, fontweight='bold')
    ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.legend(fontsize=10)
    
    if all_procs:
        ax2.set_xticks(sorted(all_procs))
    
    plt.tight_layout()
    filename = f'{output_dir}/hybrid_scaling_speedup.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved: {filename}")
    plt.close()

def print_summary(data):
    """
    Print summary statistics.
    """
    print("\n" + "="*80)
    print("HYBRID SCALING BENCHMARK SUMMARY")
    print("="*80)
    
    tile_sizes = sorted(data.keys())
    
    for tile_size in tile_sizes:
        print(f"\n{'='*80}")
        print(f"TILE SIZE: {tile_size}×{tile_size}")
        print(f"{'='*80}")
        
        configs = data[tile_size]
        
        # Phase 1
        print(f"\nPhase 1: Fixed 4 Processes, Scaling Threads")
        print(f"{'-'*80}")
        print(f"{'Threads':<15} {'Time (s)':<15} {'Speedup vs 4t':<20} {'Efficiency':<15}")
        print(f"{'-'*80}")
        
        baseline_time = configs.get((4, 4), None)
        
        phase1 = {}
        for (procs, threads), time_val in configs.items():
            if procs == 4:
                phase1[threads] = time_val
        
        for threads in sorted(phase1.keys()):
            time_val = phase1[threads]
            if baseline_time:
                speedup = baseline_time / time_val
                efficiency = (speedup / (threads / 4)) * 100
                print(f"{threads:<15} {time_val:<15.2f} {speedup:<20.2f}x {efficiency:<15.1f}%")
            else:
                print(f"{threads:<15} {time_val:<15.2f}")
        
        # Phase 2
        print(f"\nPhase 2: Fixed 4 Threads, Scaling Processes")
        print(f"{'-'*80}")
        print(f"{'Processes':<15} {'Time (s)':<15} {'Speedup vs 4p':<20} {'Efficiency':<15}")
        print(f"{'-'*80}")
        
        phase2 = {}
        for (procs, threads), time_val in configs.items():
            if threads == 4:
                phase2[procs] = time_val
        
        for procs in sorted(phase2.keys()):
            time_val = phase2[procs]
            if baseline_time:
                speedup = baseline_time / time_val
                efficiency = (speedup / (procs / 4)) * 100
                print(f"{procs:<15} {time_val:<15.2f} {speedup:<20.2f}x {efficiency:<15.1f}%")
            else:
                print(f"{procs:<15} {time_val:<15.2f}")

if __name__ == '__main__':
    # Parse the hybrid scaling output
    output_file = 'results/hybrid_scaling_24046807.out'
    
    print(f"Parsing {output_file}...")
    data = parse_hybrid_scaling_output(output_file)
    
    if not data:
        print("ERROR: Could not parse hybrid scaling output file!")
        sys.exit(1)
    
    print(f"Found {len(data)} tile sizes with configurations")
    
    # Print summary
    print_summary(data)
    
    # Create plots
    print("\n" + "="*80)
    print("Generating plots...")
    print("="*80)
    create_scaling_plots(data, 'results')
    create_comparison_plot(data, 'results')
    create_speedup_plot(data, 'results')
    
    print("\n✓ All plots generated successfully!")
