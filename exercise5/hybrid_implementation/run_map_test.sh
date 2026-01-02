#!/bin/bash
#SBATCH --job-name=map_hybrid_test
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=map_log/map_hybrid_test_%j.out
#SBATCH --error=map_log/map_hybrid_test_%j.err
#SBATCH --exclusive

# --- Create log directory ---
mkdir -p map_log

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge

# Intel MPI (commented - Linaro Forge requires GCC/OpenMPI)
# module load intel-compilers/2023.2.1
# module load impi/2021.10.0-intel-compilers-2023.2.1

module load OpenMPI/4.1.6-GCC-13.2.0
# module load Score-P/8.4-gompi-2024a-CUDA-12.6.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

# --- OpenMP settings ---
export OMP_PROC_BIND=close
export OMP_PLACES=cores
export OMP_NUM_THREADS=4

# --- Score-P settings ---
# export SCOREP_ENABLE_TRACING=1
# export SCOREP_TOTAL_MEMORY=2G
# export SCOREP_EXPERIMENT_DIRECTORY=scorep_traces_map
# export SCOREP_FILTERING_FILE=scorep.filt

# --- Build ---
echo "Building the executable..."
make clean
make

# --- Run with Map profiling (2-24 MPI ranks × 4 threads = 8-96 total cores) ---
# Fixed: 4 OpenMP threads per rank, scaling number of ranks
for ((mpi_ranks=2; mpi_ranks<=24; mpi_ranks+=1)); do
  total_cores=$((mpi_ranks * OMP_NUM_THREADS))
  echo "Running map test with ${mpi_ranks} MPI ranks × ${OMP_NUM_THREADS} threads = ${total_cores} total cores..."
  map --profile mpirun -np ${mpi_ranks} --map-by ppr:${mpi_ranks}:node:PE=${OMP_NUM_THREADS} --bind-to core ./snowman 1024 4 16
done

echo "Map profiling test completed!"
