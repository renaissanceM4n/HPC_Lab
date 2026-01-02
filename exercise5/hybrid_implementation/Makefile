# Compiler and flags for GCC with OpenMPI and Score-P
CXX = mpic++
CXXFLAGS = -O3 -std=c++17 -fopenmp -g
# scorep --instrument-filter=scorep.filt 

# Intel MPI Compiler (commented out, switch back if needed)
# CXX = scorep --instrument-filter=scorep.filt mpiicpx
# CXXFLAGS = -O3 -std=c++17 -qopenmp -xHost

# Intel MPI Process Pinning (commented out)
#MPIFLAGS = -I_MPI_PIN=on -I_MPI_PIN_RESPECT_CPUSET=on -I_MPI_PIN_RESPECT_HCA=on \
           -I_MPI_PIN_CELL=unit -I_MPI_PIN_DOMAIN=auto:compact -I_MPI_PIN_ORDER=bunch

# Source files
SRCS = main.cpp raytracer.cpp scene.cpp
OBJS = $(SRCS:.cpp=.o)

# Target executable
TARGET = snowman

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
