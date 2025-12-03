#!/bin/bash
#SBATCH --job-name=hybrid_scaling         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --cpus-per-task=8                 
#SBATCH --output=hybrid_scaling_%j.out    
#SBATCH --error=hybrid_scaling_%j.err     
#SBATCH --time=01:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive 

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0

echo "Building snowman_collapse (with collapse(2))..."
g++ -fopenmp main.cpp raytracer.cpp scene.cpp -o snowman_collapse

echo "Building snowman_no_collapse (without collapse(2))..."
cp raytracer.cpp raytracer.cpp.bak || exit 1

sed -i 's/collapse(2)//' raytracer.cpp

if g++ -fopenmp main.cpp raytracer.cpp scene.cpp -o snowman_no_collapse; then
    echo "Build succeeded"
else
    echo "Build failed! Restoring raytracer.cpp..."
fi

mv raytracer.cpp.bak raytracer.cpp
echo "Build completed."
echo ""
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# NUMA binding - all threads on NUMA domain 0
NUMA_BIND="numactl --membind=0 --cpunodebind=0"

# Scenario A: Fix Processes = 2, Increase Threads (1, 2, 4, 8)
echo "Starting Scenario A: 2 Processes, vary Threads..."
for threads in 1 2 4 8
do
    export OMP_NUM_THREADS=$threads
    echo "Running 2 Processes × $threads Threads (collapse)..."
    time $NUMA_BIND mpirun -n 2 ./snowman_collapse 1024 4
    
    echo "Running 2 Processes × $threads Threads (no_collapse)..."
    time $NUMA_BIND mpirun -n 2 ./snowman_no_collapse 1024 4
done

# Scenario B: Fix Threads = 2, Increase Processes (1, 2, 4, 8)
echo "Starting Scenario B: 2 Threads, vary Processes..."
export OMP_NUM_THREADS=2
for procs in 1 2 4 8
do
    echo "Running $procs Processes × 2 Threads (collapse)..."
    time $NUMA_BIND mpirun -n $procs ./snowman_collapse 1024 4
    
    echo "Running $procs Processes × 2 Threads (no_collapse)..."
    time $NUMA_BIND mpirun -n $procs ./snowman_no_collapse 1024 4
done

echo "Hybrid scaling tests completed."
