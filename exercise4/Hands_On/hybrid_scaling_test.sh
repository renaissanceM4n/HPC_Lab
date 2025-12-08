#!/bin/bash
#SBATCH --job-name=hybrid_scaling_intel         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=12                              
#SBATCH --output=hybrid_scaling_%j.out    
#SBATCH --error=hybrid_scaling_%j.err     
#SBATCH --time=00:30:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive 

unset SLURM_EXPORT_ENV

module load intel-compilers/2023.2.1
module load  impi/2021.10.0-intel-compilers-2023.2.1
# Clean and build
make clean
make

echo ""
echo "Build completed."
echo ""

# OpenMP settings
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# Intel MPI Process Pinning settings
export I_MPI_PIN=on
export I_MPI_PIN_RESPECT_CPUSET=on
export I_MPI_PIN_RESPECT_HCA=on
export I_MPI_PIN_CELL=unit
export I_MPI_PIN_DOMAIN=omp:compact
export I_MPI_PIN_ORDER=compact
export I_MPI_DEBUG=5

# Problem size and snowmen count
problem_size=1024
snowmen=4

# Create report directory
mkdir -p results

# Define test configurations
declare -a PROCS=(4 12 1)
declare -a THREADS=(3 1 12)

# Run tests
for i in "${!PROCS[@]}"
do
    procs=${PROCS[$i]}
    threads=${THREADS[$i]}
    export OMP_NUM_THREADS=$threads
    
    echo ""
    echo "=========================================="
    echo "Test: $procs Processes × $threads Threads"
    echo "=========================================="
    
    echo "Running $procs Processes × $threads Threads (collapse)..."
    time mpirun -np $procs \
        ./snowman_collapse $problem_size $snowmen

    echo "Running $procs Processes × $threads Threads (no_collapse)..."
    time mpirun -np $procs \
        ./snowman_no_collapse $problem_size $snowmen
done

echo ""
echo "Hybrid scaling tests completed."
