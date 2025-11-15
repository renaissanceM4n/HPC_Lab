#!/bin/bash
#SBATCH --job-name=strong_scaling         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --cpus-per-task=1                 
#SBATCH --output=strong_scaling_%j.out    
#SBATCH --error=strong_scaling_%j.err     
#SBATCH --time=01:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

# Clean and build
make clean
make

# Strong scaling test (fixed problem size: 1024 4)
echo "Starting Strong Scaling Tests..."

# Array of process counts to test
processes=(1 2 4 8 16 32 64 96)

# Run tests for each process count
for n in "${processes[@]}"
do
    echo "Running test with $n processes..."
    
    
    time mpirun -n $n ./snowman 1024 4
done

echo "Strong scaling tests completed."
