#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import sys

def parse_benchmark_output(filename):
    """
    Parse tile_benchmark_hybrid_*.out file and extract timing data.
    Returns a dict with structure:
    {(processes, threads): {tile_size: max_time}}
    """
    data = defaultdict(dict)
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find all configuration blocks
    config_pattern = r'Configuration:\s*(\d+)\s*Processes\s*×\s*(\d+)\s*Threads.*?(?=Configuration:|$)'
    
    for config_match in re.finditer(config_pattern, content, re.DOTALL):
        procs = int(config_match.group(1))
        threads = int(config_match.group(2))
        config_block = config_match.group(0)
        
        # Find tile sizes within this configuration
        tile_pattern = r'Tile Size:\s*(\d+)x\d+.*?Max Local Computation Time.*?:\s*([\d.]+)\s*seconds'
        
        for tile_match in re.finditer(tile_pattern, config_block, re.DOTALL):
            tile_size = int(tile_match.group(1))
            max_time = float(tile_match.group(2))
            
            key = (procs, threads)
            data[key][tile_size] = max_time
    
    return data

def create_plots(data, output_dir='results'):
    """
    Create three separate plots for each process/thread configuration.
    """
    # Group data by configuration
    configs = sorted(data.keys())
    
    # Define colors for tile sizes
    tile_sizes = sorted(set(size for config in data.values() for size in config.keys()))
    colors = plt.cm.tab10(np.linspace(0, 1, len(tile_sizes)))
    color_map = {size: colors[i] for i, size in enumerate(tile_sizes)}
    
    # Create a plot for each configuration
    for config_idx, (procs, threads) in enumerate(configs):
        fig, ax = plt.subplots(figsize=(10, 6))
        
        times = data[(procs, threads)]
        tile_sizes_config = sorted(times.keys())
        exec_times = [times[size] for size in tile_sizes_config]
        
        # Create bar plot
        x_pos = np.arange(len(tile_sizes_config))
        bars = ax.bar(x_pos, exec_times, 
                      color=[color_map[size] for size in tile_sizes_config],
                      alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar, time_val in zip(bars, exec_times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{time_val:.1f}s',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Customize plot
        ax.set_xlabel('Tile Size (pixels)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title(f'Tile Size Impact: {procs} Processes × {threads} Threads\n(Total: {procs*threads} cores)', 
                    fontsize=13, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f'{size}×{size}' for size in tile_sizes_config], fontsize=11)
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Add reference line for best performance
        min_time = min(exec_times)
        ax.axhline(y=min_time, color='red', linestyle='--', linewidth=2, 
                  label=f'Best: {min_time:.1f}s', alpha=0.7)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        
        # Save with descriptive filename
        filename = f'{output_dir}/tile_benchmark_{procs}p_{threads}t.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()

def create_comparison_plot(data, output_dir='results'):
    """
    Create a comparison plot showing performance across all configurations.
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    configs = sorted(data.keys())
    x_labels = [f'{p}p×{t}t' for p, t in configs]
    
    # Get all tile sizes
    all_tile_sizes = sorted(set(size for config in data.values() for size in config.keys()))
    
    # Prepare data for grouped bar chart
    x_pos = np.arange(len(configs))
    width = 0.15
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(all_tile_sizes)))
    
    for i, tile_size in enumerate(all_tile_sizes):
        times = [data[config].get(tile_size, 0) for config in configs]
        offset = (i - len(all_tile_sizes)/2 + 0.5) * width
        bars = ax.bar(x_pos + offset, times, width, 
                     label=f'Tile {tile_size}×{tile_size}',
                     color=colors[i], alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Add value labels
        for bar, time_val in zip(bars, times):
            if time_val > 0:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{time_val:.0f}',
                       ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Configuration (Processes × Threads)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Tile Size Benchmark: Cross-Configuration Comparison', fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, fontsize=11)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.5)
    
    plt.tight_layout()
    
    filename = f'{output_dir}/tile_benchmark_comparison.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved: {filename}")
    plt.close()

def print_summary(data):
    """
    Print summary statistics.
    """
    print("\n" + "="*70)
    print("TILE BENCHMARK SUMMARY")
    print("="*70)
    
    for config in sorted(data.keys()):
        procs, threads = config
        times = data[config]
        
        print(f"\nConfiguration: {procs} Processes × {threads} Threads (Total: {procs*threads} cores)")
        print("-" * 70)
        print(f"{'Tile Size':<15} {'Time (s)':<15} {'Relative to Best':<20}")
        print("-" * 70)
        
        min_time = min(times.values())
        
        for tile_size in sorted(times.keys()):
            time_val = times[tile_size]
            relative = time_val / min_time
            print(f"{tile_size}×{tile_size:<10} {time_val:<15.2f} {relative:<20.2f}x")
        
        print(f"\nBest tile size: {max(times, key=lambda k: 1/times[k])}×{max(times, key=lambda k: 1/times[k])} ({min_time:.2f}s)")

if __name__ == '__main__':
    # Parse the benchmark output
    output_file = 'results/tile_benchmark_hybrid_24044148.out'
    
    print(f"Parsing {output_file}...")
    data = parse_benchmark_output(output_file)
    
    if not data:
        print("ERROR: Could not parse benchmark output file!")
        sys.exit(1)
    
    print(f"Found {len(data)} configurations")
    
    # Print summary
    print_summary(data)
    
    # Create plots
    print("\nGenerating plots...")
    create_plots(data, 'results')
    create_comparison_plot(data, 'results')
    
    print("\n✓ All plots generated successfully!")
