#!/bin/bash
#SBATCH --job-name=hybrid_scaling         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --cpus-per-task=1                
#SBATCH --output=hybrid_scaling_%j.out    
#SBATCH --error=hybrid_scaling_%j.err     
#SBATCH --time=01:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive 

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

# Clean and build
make clean
make

echo ""
echo "Build completed."
echo ""

# OpenMP settings
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# -------------------------------
# Test 1: Fix processes to 4, vary threads (4, 8, 12, 16)
# -------------------------------
echo "TEST 1: Fixed 4 Processes, Varying Threads"
echo "=========================================="
procs=4
for threads in 4 8 12 16
do
    export OMP_NUM_THREADS=$threads
    
    echo "Running $procs Processes × $threads Threads (collapse)..."
    time mpirun -np $procs \
        --map-by ppr:$procs:node \
        --bind-to numa \
        --report-bindings \
        ./snowman_collapse 1024 4

    echo "Running $procs Processes × $threads Threads (no_collapse)..."
    time mpirun -np $procs \
        --map-by ppr:$procs:node \
        --bind-to numa \
        --report-bindings \
        ./snowman_no_collapse 1024 4
done

# -------------------------------
# Test 2: Fix threads to 4, vary processes (4, 8, 12, 16)
# -------------------------------
echo ""
echo "TEST 2: Fixed 4 Threads, Varying Processes"
echo "=========================================="
threads=4
export OMP_NUM_THREADS=$threads

for procs in 4 8 12 16
do
    echo "Running $procs Processes × $threads Threads (collapse)..."
    time mpirun -np $procs \
        --map-by ppr:$procs:node \
        --bind-to numa \
        --report-bindings \
        ./snowman_collapse 1024 4

    echo "Running $procs Processes × $threads Threads (no_collapse)..."
    time mpirun -np $procs \
        --map-by ppr:$procs:node \
        --bind-to numa \
        --report-bindings \
        ./snowman_no_collapse 1024 4
done

echo ""
echo "Hybrid scaling tests completed."