#!/bin/bash
#SBATCH --job-name=tile_benchmark         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --cpus-per-task=1                 
#SBATCH --output=tile_benchmark_%j.out    
#SBATCH --error=tile_benchmark_%j.err     
#SBATCH --time=02:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive 

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

# Clean and build
make clean
make

# Tile size benchmark test (fixed problem size: 1024 4, varying tile sizes)
echo "Starting Tile Size Benchmark Tests..."

# Run tests for each tile size (32, 64, 128, 256) at 96 processes
for tile_size in 8 16 32 48 64 128
do
    echo ""
    echo "Running test with tile size ${tile_size}x${tile_size} at 96 processes..."
    
    time mpirun -n 96 ./snowman 1024 4 $tile_size
done

echo "Tile size benchmark tests completed."
