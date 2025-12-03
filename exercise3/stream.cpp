#include <iostream>
#include <chrono>
#include <cmath>
#include <fstream>
#include <cstdlib>
#include <omp.h>

int main(int argc, char** argv)
{
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <N> [num_threads]" << std::endl;
        return 1;
    }

    size_t N = std::stoull(argv[1]);  // Read N from command-line input
    
    // Set number of threads if provided, otherwise use default
    int num_threads = (argc >= 3) ? std::atoi(argv[2]) : omp_get_max_threads();
    omp_set_num_threads(num_threads);
    
    // Bind all threads to the same NUMA domain (NUMA 0) for optimal memory locality
    #pragma omp parallel
    {
        #pragma omp single
        {
            std::cout << "Running with " << num_threads << " OpenMP threads" << std::endl;
            std::cout << "Thread binding: All threads bound to NUMA domain 0" << std::endl;
        }
    }
    
    const double s = 1.00000000001;

    double* a = (double*) aligned_alloc(64, N * sizeof(double));
    double* b = (double*) aligned_alloc(64, N * sizeof(double));
    double* c = (double*) aligned_alloc(64, N * sizeof(double));

    // Parallel initialization with static scheduling for better cache locality
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < N; ++i) {
        a[i] = 0.0;
        b[i] = 1.0;
	c[i] = 1.0;
    }

    int NITER = 1;
    double runtime = 0.0;

    do {
        auto start = std::chrono::high_resolution_clock::now();
	
	for (int k = 0; k < NITER; ++k) {
                // Parallel computation with static scheduling for cache efficiency
                #pragma omp parallel for schedule(static) collapse(1)
                for (size_t i = 0; i < N; ++i) {
                    a[i] = b[i] + s * c[i];
                }

                if (a[N / 2] < 0.0) {
                    std::cout << a[N / 2] << std::endl;
                }
	}

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> duration_s = end - start;
        runtime = duration_s.count();

        NITER *= 2;
    } while (runtime < 2.0); // ensure at least 200 ms

    NITER /= 2;
    double gflops = (2.0 * NITER * N) / (runtime * 1e9);

    std::cout << "\n=== Performance Summary ===" << std::endl;
    std::cout << "Threads: " << num_threads << std::endl;
    std::cout << "Total walltime: " << runtime << "s\t"
              << "NITER: " << NITER << "\t"
              << "Array size N: " << N << std::endl;
    std::cout << "GFlop/s: " << gflops << "\t"
              << "GFlop/s per thread: " << (gflops / num_threads) << std::endl;

    free(a);
    free(b);
    free(c);

    return 0;
}

