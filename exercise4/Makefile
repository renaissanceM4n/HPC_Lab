# Compiler and flags for Intel Compiler with Intel MPI
CXX = mpiicpx
CXXFLAGS = -O3 -std=c++17 -qopenmp -xHost

# Intel MPI Process Pinning (default settings)
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
