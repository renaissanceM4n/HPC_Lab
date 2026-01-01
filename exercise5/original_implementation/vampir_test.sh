#!/bin/bash
#SBATCH --job-name=vampir_hybrid_test
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=vampir_hybrid_test_%j.out
#SBATCH --error=vampir_hybrid_test_%j.err
#SBATCH --exclusive

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge
module load GCCcore/12.2.0
module load OpenMPI/4.1.5-GCC-12.2.0
module load intel-compilers/2023.2.1
module load impi/2021.10.0-intel-compilers-2023.2.1
module load Score-P/8.4-gompi-2024a-CUDA-12.6.0

# --- Intel MPI Modules (commented out, switch back if needed) ---
# module load intel-compilers/2023.2.1
# module load impi/2021.10.0-intel-compilers-2023.2.1

# # --- OpenMP settings ---
# export OMP_PROC_BIND=close
# export OMP_PLACES=cores
# export OMP_NUM_THREADS=4

# --- Intel MPI Process Pinning settings (commented out for GCC/OpenMPI) ---
# export I_MPI_PIN=on
# export I_MPI_PIN_RESPECT_CPUSET=on
# export I_MPI_PIN_RESPECT_HCA=on
# export I_MPI_PIN_CELL=unit
# export I_MPI_PIN_DOMAIN=omp
# export I_MPI_PIN_ORDER=compact

processes=96

# --- Score-P settings ---
export SCOREP_ENABLE_TRACING=1
export SCOREP_TOTAL_MEMORY=2G
export SCOREP_EXPERIMENT_DIRECTORY=scorep_traces_original/test_p_${processes}
export SCOREP_FILTERING_FILE=scorep.filt

# --- Build ---

make clean
make

# --- Run with Score-P tracing (96 MPI processes × 4 OpenMP threads = 384 total threads) ---
# OpenMPI binding for hybrid MPI+OpenMP
mpirun -n $processes ./snowman 1024 4 