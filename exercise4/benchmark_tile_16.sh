#!/bin/bash
#SBATCH --job-name=tile_16_benchmark
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --cpus-per-task=1
#SBATCH --output=tile_16_benchmark_%j.out
#SBATCH --error=tile_16_benchmark_%j.err
#SBATCH --time=00:30:00
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

# Clean and build
make clean
make

# Tile 16x16 benchmark test (fixed problem size: 1024 4, tile size: 16, 96 processes)
echo "Starting Tile 16x16 Benchmark with 96 Processes..."

echo ""
echo "Running test with tile size 16x16 at 96 processes..."

mpirun -n 96 ./snowman 1024 4 16

echo "Tile 16x16 benchmark test completed."
