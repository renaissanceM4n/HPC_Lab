#!/bin/bash
#SBATCH --job-name=hybrid_scaling_perf         
#SBATCH --account=tmp_hpca_workshop
#SBATCH --nodes=1                         
#SBATCH --ntasks-per-node=96              
#SBATCH --cpus-per-task=1                
#SBATCH --output=hybrid_scaling_perf_%j.out    
#SBATCH --error=hybrid_scaling_perf_%j.err     
#SBATCH --time=01:00:00                   
#SBATCH --partition=intelsr_devel
#SBATCH --exclusive 

unset SLURM_EXPORT_ENV

module load OpenMPI/4.1.6-GCC-13.2.0
module load LinaroForge/25.0.3-GCCcore-13.2.0-linux-x86_64

# Clean and build
make clean
make

echo ""
echo "Build completed."
echo ""

# OpenMP settings
export OMP_PROC_BIND=close
export OMP_PLACES=cores

# Problem size and snowmen count
problem_size=1024
snowmen=4
procs=4
threads=16

export OMP_NUM_THREADS=$threads

echo "Running $procs Processes × $threads Threads (collapse)..."
perf-report mpirun -np $procs \
    --map-by ppr:$procs:node \
    --bind-to numa \
    --report-bindings \
    ./snowman_collapse $problem_size $snowmen

echo ""
echo "Test completed."
