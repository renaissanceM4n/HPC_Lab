#!/bin/bash
#SBATCH --job-name=strong_scaling_fixed_threads
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=scoreP_logs/strong_scaling_scoreP_fixed_threads_%j.out
#SBATCH --error=scoreP_logs/strong_scaling_scoreP_fixed_threads_%j.err
#SBATCH --exclusive

# --- Create log directory ---
mkdir -p scoreP_logs

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge
module load GCCcore/12.2.0
module load OpenMPI/4.1.5-GCC-12.2.0
module load Score-P/8.4-gompi-2024a-CUDA-12.6.0

# --- OpenMP settings ---
export OMP_PROC_BIND=close
export OMP_PLACES=cores
export OMP_NUM_THREADS=4

# --- Score-P settings ---
export SCOREP_ENABLE_TRACING=1
export SCOREP_TOTAL_MEMORY=2G
export SCOREP_FILTERING_FILE=scorep.filt

# --- Build ---
make clean
make

# --- Run strong scaling with fixed 4 threads per process ---
for p in {1..24}; do
    echo "Run: ${p} processes × 4 threads"
    
    # Set Score-P directory dynamically based on process count
    export SCOREP_EXPERIMENT_DIRECTORY=scorep_traces_hybrid/strong_scaling_p_${p}_t_${OMP_NUM_THREADS}
    
    mpirun -n ${p} --map-by ppr:${p}:node:PE=${OMP_NUM_THREADS} --bind-to core ./snowman 1024 4 16
done
