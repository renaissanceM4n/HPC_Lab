#!/usr/bin/env python3
"""
Parse MAP profiling logs and generate strong scaling comparison plot
for Original (pure MPI) vs. Hybrid (MPI+OpenMP) implementations.
"""

import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path

def parse_map_out_file(filepath):
    """
    Parse MAP .out file and extract (workers, profiling_time) pairs.
    For original: workers = MPI processes
    For hybrid: workers = MPI processes * 4 threads
    """
    data = []
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern: "MPI Processes: <N>" followed by "Max Local Computation Time (across all ranks): <time> seconds"
    pattern = r'MPI Processes:\s+(\d+).*?Max Local Computation Time \(across all ranks\):\s+([\d.]+)\s+seconds'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for mpi_procs, max_time in matches:
        data.append((int(mpi_procs), float(max_time)))
    
    return data

def parse_map_err_file(filepath):
    """
    Parse MAP .err file and extract profiling time (MPI init to finalize).
    Returns dict: {mpi_procs: profiling_time}
    """
    data = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    current_procs = None
    for i, line in enumerate(lines):
        # Look for "Profiling ... : mpirun -n <N>" or "mpirun -np <N>"
        match_n = re.search(r'mpirun -n (\d+)', line)
        match_np = re.search(r'mpirun -np (\d+)', line)
        if match_n:
            current_procs = int(match_n.group(1))
        elif match_np:
            current_procs = int(match_np.group(1))
        
        # Look for "Profiling time: <time> seconds"
        if current_procs and 'Profiling time:' in line:
            match_time = re.search(r'Profiling time:\s+(\d+)', line)
            if match_time:
                data[current_procs] = int(match_time.group(1))
                current_procs = None  # reset
    
    return data

# Parse original implementation (pure MPI)
original_out = parse_map_out_file('original_implementation/map_log/map_original_test_24213527.out')
original_err = parse_map_err_file('original_implementation/map_log/map_original_test_24213527.err')

# Parse hybrid implementation (MPI + OpenMP, 4 threads per process)
hybrid_out = parse_map_out_file('hybrid_implementation/map_log/map_hybrid_test_24213952.out')
hybrid_err = parse_map_err_file('hybrid_implementation/map_log/map_hybrid_test_24213952.err')

# Prepare data for plotting
# Original: workers = MPI ranks (1 thread each)
original_workers = []
original_times_max = []
original_times_prof = []

for mpi_procs, max_time in sorted(original_out):
    original_workers.append(mpi_procs)
    original_times_max.append(max_time)
    original_times_prof.append(original_err.get(mpi_procs, max_time))

# Hybrid: workers = MPI ranks * 4 threads
hybrid_workers = []
hybrid_times_max = []
hybrid_times_prof = []

for mpi_procs, max_time in sorted(hybrid_out):
    hybrid_workers.append(mpi_procs * 4)  # 4 threads per process
    hybrid_times_max.append(max_time)
    hybrid_times_prof.append(hybrid_err.get(mpi_procs, max_time))

# Convert to numpy arrays
original_workers = np.array(original_workers)
original_times_max = np.array(original_times_max)
original_times_prof = np.array(original_times_prof)

hybrid_workers = np.array(hybrid_workers)
hybrid_times_max = np.array(hybrid_times_max)
hybrid_times_prof = np.array(hybrid_times_prof)

# Create figure with single plot
fig, ax = plt.subplots(figsize=(10, 6))

# --- Plot: Max Local Computation Time (per-rank work) ---
ax.plot(original_workers, original_times_max, 'o-', label='Original (pure MPI)', linewidth=2, markersize=6)
ax.plot(hybrid_workers, hybrid_times_max, 's-', label='Hybrid (MPI+OpenMP)', linewidth=2, markersize=6)

# Ideal scaling reference (from first original datapoint)
if len(original_workers) > 0 and len(original_times_max) > 0:
    ref_workers = original_workers[0]
    ref_time = original_times_max[0]
    ideal_workers = np.linspace(original_workers[0], max(max(original_workers), max(hybrid_workers)), 50)
    ideal_times = ref_time * ref_workers / ideal_workers
    ax.plot(ideal_workers, ideal_times, 'k--', alpha=0.5, label='Ideal scaling', linewidth=1.5)

ax.set_xlabel('Total Workers (MPI ranks or MPI×threads)', fontsize=13)
ax.set_ylabel('Max Local Computation Time (s)', fontsize=13)
ax.set_title('Strong Scaling: Max Per-Rank Computation Time', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('map_strong_scaling_comparison.pdf', dpi=300, bbox_inches='tight')
plt.savefig('map_strong_scaling_comparison.png', dpi=300, bbox_inches='tight')
print(f"Plot saved: map_strong_scaling_comparison.pdf/png")

# Print summary statistics
print("\n=== Summary Statistics ===")
print(f"Original: {len(original_workers)} configurations tested (workers: {original_workers[0]} to {original_workers[-1]})")
print(f"Hybrid:   {len(hybrid_workers)} configurations tested (workers: {hybrid_workers[0]} to {hybrid_workers[-1]})")
print(f"\nAt 96 workers:")
idx_orig_96 = np.where(original_workers == 96)[0]
idx_hybrid_96 = np.where(hybrid_workers == 96)[0]
if len(idx_orig_96) > 0 and len(idx_hybrid_96) > 0:
    print(f"  Original: Max compute = {original_times_max[idx_orig_96[0]]:.1f}s, Profiling time = {original_times_prof[idx_orig_96[0]]:.1f}s")
    print(f"  Hybrid:   Max compute = {hybrid_times_max[idx_hybrid_96[0]]:.1f}s, Profiling time = {hybrid_times_prof[idx_hybrid_96[0]]:.1f}s")
    speedup = original_times_prof[idx_orig_96[0]] / hybrid_times_prof[idx_hybrid_96[0]]
    print(f"  Speedup (profiling time): {speedup:.2f}×")
