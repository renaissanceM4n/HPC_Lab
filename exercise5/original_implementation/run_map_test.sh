#!/bin/bash
#SBATCH --job-name=map_original_test
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=map_original_test_%j.out
#SBATCH --error=map_original_test_%j.err
#SBATCH --exclusive

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge

# Intel MPI (commented - Linaro Forge requires GCC/OpenMPI)
# module load intel-compilers/2023.2.1
# module load impi/2021.10.0-intel-compilers-2023.2.1

module load OpenMPI/4.1.6-GCC-13.2.0
# module load Score-P/8.4-gompi-2024a-CUDA-12.6.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64



# --- Score-P settings ---
# export SCOREP_ENABLE_TRACING=1
# export SCOREP_TOTAL_MEMORY=2G
# export SCOREP_EXPERIMENT_DIRECTORY=scorep_traces_map
# export SCOREP_FILTERING_FILE=scorep.filt

# --- Build ---
echo "Building the executable..."
make clean
make

# --- Run with Map profiling (96 MPI processes) ---
echo "Running map test with profiling (96 processes)..."
map --profile mpirun -n 96 ./snowman 1024 4

echo "Map profiling test completed!"
