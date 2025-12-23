#!/bin/bash
#SBATCH --job-name=vampir_test
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=vampir_test_%j.out
#SBATCH --error=vampir_test_%j.err
#SBATCH --exclusive

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge
module load GCCcore/12.2.0
module load OpenMPI/4.1.5-GCC-12.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64
module load Score-P/8.4-gompi-2024a-CUDA-12.6.0

export SCOREP_EXPERIMENT_DIRECTORY=scorep_traces
export SCOREP_ENABLE_TRACING=1
export SCOREP_TOTAL_MEMORY=2G
export SCOREP_FILTERING_FILE=scorep.filt

# --- Build ---

make clean
make

# --- Run with Score-P tracing (generates OTF2 files) ---
mpirun -n 8 ./snowman 1024 4 8