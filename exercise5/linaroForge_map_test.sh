#!/bin/bash
#SBATCH --job-name=profile_scaling
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --output=profile_scaling_%j.out
#SBATCH --error=profile_scaling_%j.err
#SBATCH --exclusive

# --- Environment setup ---
unset SLURM_EXPORT_ENV
module purge
module load GCCcore/12.2.0
module load OpenMPI/4.1.5-GCC-12.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

# --- Build ---

make clean
make

map --profile mpirun -n 48 ./snowman