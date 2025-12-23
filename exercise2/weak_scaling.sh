#!/bin/bash
#SBATCH --job-name=weak_scaling            
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                          
#SBATCH --ntasks-per-node=96              # Number of MPI tasks per node (maximum we'll use)
#SBATCH --cpus-per-task=1                 # Number of threads per task
#SBATCH --output=weak_scaling_%j.out     
#SBATCH --error=weak_scaling_%j.err       
#SBATCH --time=01:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

# Clean and build
make clean
make

# Weak scaling test
echo "Starting Weak Scaling Tests..."

# Array of process counts and corresponding problem sizes
processes=(1 4 16 64)
pixels=(128 256 512 1024)

# Run tests for each process count
for i in {0..3}
do
    n=${processes[$i]}
    p=${pixels[$i]}
    echo "Running test with $n processes..."
    
    time mpirun -n $n ./snowman $p 3
done

echo "Weak scaling tests completed."