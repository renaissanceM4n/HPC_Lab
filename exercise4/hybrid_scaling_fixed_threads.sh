#!/bin/bash
#SBATCH --job-name=hybrid_scaling_fixed_threads         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --output=hybrid_scaling_fixed_threads_%j.out    
#SBATCH --error=hybrid_scaling_fixed_threads_%j.err     
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
# export OMP_DISPLAY_AFFINITY=True

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

# Tile sizes to test
declare -a TILE_SIZES=(64 128)

# Fixed thread counts to test with corresponding process scales to reach 96 cores
# 12 threads: 4, 6, 8 processes (48, 72, 96 cores)
# 8 threads: 4, 8, 12 processes (32, 64, 96 cores)

# Create results directory
mkdir -p results

echo "=========================================="
echo "Hybrid Scaling: Fixed Threads - Varying Processes"
echo "=========================================="
echo "Testing tile sizes: 64, 128"
echo ""
echo "Configuration 1: 12 Fixed Threads, Scaling Processes"
echo "  Processes: 4, 6, 8 (scaling to 96 cores)"
echo ""
echo "Configuration 2: 8 Fixed Threads, Scaling Processes"
echo "  Processes: 4, 8, 12 (scaling to 96 cores)"
echo ""

# Test each tile size
for tile_size in "${TILE_SIZES[@]}"
do
    echo ""
    echo "======================================================================"
    echo "TILE SIZE: ${tile_size}x${tile_size}"
    echo "======================================================================"
    echo ""
    
    # Configuration 1: 12 Fixed Threads, Scaling Processes (4, 6, 8)
    echo "=== 12 Fixed Threads, Scaling Processes (Tile ${tile_size}x${tile_size}) ==="
    declare -a PROCS_12T=(4 6 8)
    for procs in "${PROCS_12T[@]}"
    do
        threads=12
        total_cores=$((procs * threads))
        
        export OMP_NUM_THREADS=$threads
        
        echo ""
        echo "=========================================="
        echo "Configuration: $procs Processes × $threads Threads (Total: $total_cores cores)"
        echo "=========================================="
        
        echo "Running $procs Processes × $threads Threads..."
        time mpirun -np $procs \
            ./snowman $problem_size $snowmen $tile_size

        echo ""
    done

    # Configuration 2: 8 Fixed Threads, Scaling Processes (4, 8, 12)
    echo ""
    echo "=== 8 Fixed Threads, Scaling Processes (Tile ${tile_size}x${tile_size}) ==="
    declare -a PROCS_8T=(4 8 12)
    for procs in "${PROCS_8T[@]}"
    do
        threads=8
        total_cores=$((procs * threads))
        
        export OMP_NUM_THREADS=$threads
        
        echo ""
        echo "=========================================="
        echo "Configuration: $procs Processes × $threads Threads (Total: $total_cores cores)"
        echo "=========================================="
        
        echo "Running $procs Processes × $threads Threads..."
        time mpirun -np $procs \
            ./snowman $problem_size $snowmen $tile_size

        echo ""
    done
done

echo ""
echo "======================================================================"
echo "Hybrid scaling tests completed."
echo "Tested all combinations of:"
echo "  Tile sizes: 64, 128"
echo "  Configuration 1: 12 Fixed Threads, Processes: 4/6/8 (up to 96 cores)"
echo "  Configuration 2: 8 Fixed Threads, Processes: 4/8/12 (up to 96 cores)"
echo "======================================================================"
