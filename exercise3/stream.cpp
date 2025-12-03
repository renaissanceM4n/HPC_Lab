#include <iostream>
#include <chrono>
#include <cmath>
#include <fstream>
#include <cstdlib>
#include <omp.h>

int main(int argc, char** argv)
{
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <N>" << std::endl;
        return 1;
    }

    size_t N = std::stoull(argv[1]);  // Read N from command-line input
    const double s = 1.00000000001;

    double* a = (double*) aligned_alloc(64, N * sizeof(double));
    double* b = (double*) aligned_alloc(64, N * sizeof(double));
    double* c = (double*) aligned_alloc(64, N * sizeof(double));
    #pragma omp parallel for
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
                #pragma omp parallel for
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

    std::cout << "Total walltime: " << runtime << "s\t"
              << "NITER: " << NITER << "\t"
              << "GFlop/s: " << gflops << "\t"
              << "Iterations: " << N << std::endl;

    free(a);
    free(b);

    return 0;
}

