#!/bin/bash
#SBATCH --job-name=hybrid_scaling_intel         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --output=hybrid_scaling_%j.out    
#SBATCH --error=hybrid_scaling_%j.err     
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
declare -a TILE_SIZES=(8 64 128)

# Create results directory
mkdir -p results

echo "=========================================="
echo "Hybrid Scaling: Dynamic - Processes × Threads"
echo "=========================================="
echo "Testing tile sizes: 8, 64, 128"
echo ""

# Scaling values in steps of 4
declare -a SCALES=(4 8 12 16 20 24)

# Test each tile size
for tile_size in "${TILE_SIZES[@]}"
do
    echo ""
    echo "======================================================================"
    echo "TILE SIZE: ${tile_size}x${tile_size}"
    echo "======================================================================"
    echo ""
    
    echo "=== Phase 1: Fixed 4 Processes, Scaling Threads (Tile ${tile_size}x${tile_size}) ==="
    for threads in "${SCALES[@]}"
    do
        procs=4
        total_tasks=$((procs * threads))
        
        export OMP_NUM_THREADS=$threads
        
        echo ""
        echo "=========================================="
        echo "Configuration: $procs Processes × $threads Threads (Total: $total_tasks)"
        echo "=========================================="
        
        echo "Running $procs Processes × $threads Threads..."
        time mpirun -np $procs \
            ./snowman $problem_size $snowmen $tile_size

        echo ""
    done

    echo ""
    echo "=== Phase 2: Fixed 4 Threads, Scaling Processes (Tile ${tile_size}x${tile_size}) ==="
    for procs in "${SCALES[@]}"
    do
        threads=4
        total_tasks=$((procs * threads))
        
        export OMP_NUM_THREADS=$threads
        
        echo ""
        echo "=========================================="
        echo "Configuration: $procs Processes × $threads Threads (Total: $total_tasks)"
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
echo "  Tile sizes: 8, 64, 128"
echo "  Phase 1: 4 fixed processes, 4/8/12/16/20/24 threads"
echo "  Phase 2: 4 fixed threads, 4/8/12/16/20/24 processes"
echo "======================================================================"
