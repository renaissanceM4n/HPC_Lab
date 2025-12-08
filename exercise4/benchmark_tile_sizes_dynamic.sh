#!/bin/bash
#SBATCH --job-name=tile_benchmark_hybrid         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --output=tile_benchmark_hybrid_%j.out    
#SBATCH --error=tile_benchmark_hybrid_%j.err     
#SBATCH --time=01:00:00                   
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

# OpenMP Thread Pinning settings
export OMP_PLACES=cores
export OMP_PROC_BIND=close
export OMP_DISPLAY_AFFINITY=True

# Intel MPI Process Pinning settings
export I_MPI_PIN=on
export I_MPI_PIN_RESPECT_CPUSET=on
export I_MPI_PIN_RESPECT_HCA=on
export I_MPI_PIN_CELL=unit
export I_MPI_PIN_DOMAIN=omp
export I_MPI_PIN_ORDER=compact
export I_MPI_DEBUG=5

# Problem size and snowmen count
problem_size=1024
snowmen=4

# Create results directory
mkdir -p results

echo "=========================================="
echo "Tile Size Benchmark with Hybrid Scaling"
echo "=========================================="
echo ""

# Tile size benchmark configurations
declare -a THREAD_CONFIGS=(3 12 24)
declare -a TILE_SIZES=(8 16 32 64 128 256)

fixed_procs=4

# Test each thread configuration with all tile sizes
for fixed_threads in "${THREAD_CONFIGS[@]}"
do
    export OMP_NUM_THREADS=$fixed_threads
    total_tasks=$((fixed_procs * fixed_threads))
    
    echo ""
    echo "=========================================="
    echo "Configuration: $fixed_procs Processes × $fixed_threads Threads (Total: $total_tasks)"
    echo "=========================================="
    echo "Testing tile sizes: 8, 16, 32, 64, 128, 256"
    echo ""
    
    for tile_size in "${TILE_SIZES[@]}"
    do
        echo "=========================================="
        echo "Tile Size: ${tile_size}x${tile_size}"
        echo "=========================================="
        
        echo "Running $fixed_procs Processes × $fixed_threads Threads..."
        time mpirun -np $fixed_procs \
            ./snowman $problem_size $snowmen $tile_size
        
        echo ""
    done
done

echo ""
echo "Tile size benchmark tests completed."
echo "Tested configurations: 4p×3t (12 tasks), 4p×12t (48 tasks), 4p×24t (96 tasks)"
echo "Results show impact of OMP parallelization on different tile granularities."
